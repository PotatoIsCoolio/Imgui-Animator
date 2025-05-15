import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from animator.animation.keyframe import AnimationKeyframe
# This was the worst part about making this whole project.
#DontAsk
class AnimatedItem(QObject):
    def __init__(self, item, name="Item"):
        super().__init__()
        self.item = item
        self.name = name
        self.keyframes = []
        self.itemType = "unknown"
        self.color = QColor(255, 255, 255)
        self.fillColor = QColor(100, 100, 255, 180)
        self.properties = {}
        self.useSmoothing = True
        
        if isinstance(item, QGraphicsItem):
            if hasattr(item, "shapeType"):
                self.itemType = item.shapeType
            elif hasattr(item, "toPlainText"):
                self.itemType = "text"
                self.properties["text"] = item.toPlainText()
                self.properties["fontSize"] = item.font().pointSize()
                self.properties["fontFamily"] = item.font().family()
                self.color = item.defaultTextColor()
    
    def addKeyframe(self, frame):
        pos = self.item.pos()
        transform = self.item.transform()
        scale = math.sqrt(transform.m11() * transform.m11() + transform.m12() * transform.m12())
        rotation = math.degrees(math.atan2(transform.m12(), transform.m11()))
        opacity = self.item.opacity()
        
        keyframe = AnimationKeyframe(
            frame, pos.x(), pos.y(), rotation, scale, opacity
        )
        
        for i, kf in enumerate(self.keyframes):
            if kf.frame == frame:
                self.keyframes[i] = keyframe
                return keyframe
        
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda kf: kf.frame)
        return keyframe
    
    def getKeyframe(self, frame):
        if not self.keyframes:
            return None
            
        for kf in self.keyframes:
            if kf.frame == frame:
                return kf
        
        prevKf = None
        nextKf = None
        
        for kf in self.keyframes:
            if kf.frame < frame:
                if prevKf is None or kf.frame > prevKf.frame:
                    prevKf = kf
            elif kf.frame > frame:
                if nextKf is None or kf.frame < nextKf.frame:
                    nextKf = kf
        
        if prevKf is None:
            return self.keyframes[0]
        if nextKf is None:
            return self.keyframes[-1]
        
        t = (frame - prevKf.frame) / (nextKf.frame - prevKf.frame)
        
        if self.useSmoothing:
            t = t * t * (3 - 2 * t)
        
        return AnimationKeyframe(
            frame,
            prevKf.x + t * (nextKf.x - prevKf.x),
            prevKf.y + t * (nextKf.y - prevKf.y),
            prevKf.rotation + t * (nextKf.rotation - prevKf.rotation),
            prevKf.scale + t * (nextKf.scale - prevKf.scale),
            prevKf.opacity + t * (nextKf.opacity - prevKf.opacity)
        )
    
    def applyKeyframe(self, keyframe):
        if not keyframe:
            return
            
        self.item.setPos(keyframe.x, keyframe.y)
        
        transform = QTransform()
        transform.rotate(keyframe.rotation)
        transform.scale(keyframe.scale, keyframe.scale)
        self.item.setTransform(transform)
        
        self.item.setOpacity(keyframe.opacity)
    
    def toDict(self):
        return {
            "name": self.name,
            "type": self.itemType,
            "color": self.color.name(QColor.HexArgb),
            "fill_color": self.fillColor.name(QColor.HexArgb),
            "properties": self.properties,
            "keyframes": [kf.toDict() for kf in self.keyframes],
            "use_smoothing": self.useSmoothing
        }
    # Fuckass python cant understand C+ yo
    def toImguiCode(self):
        code = []
        
        if not self.keyframes:
            return "// No animation data for this item\n"
        
        varName = self.name.lower().replace(" ", "_")
        
        code.append(f"// Animation data for {self.name}")
        code.append(f"struct {varName}_keyframe {{")
        code.append("    int frame;")
        code.append("    float x, y;")
        code.append("    float rotation;")
        code.append("    float scale;")
        code.append("    float opacity;")
        code.append("};")
        code.append("")
        
        code.append(f"const {varName}_keyframe {varName}_animation[] = {{")
        for kf in self.keyframes:
            code.append(f"    {{ {kf.frame}, {kf.x:.1f}f, {kf.y:.1f}f, {kf.rotation:.1f}f, {kf.scale:.2f}f, {kf.opacity:.2f}f }},")
        code.append("};")
        code.append(f"const int {varName}_keyframe_count = {len(self.keyframes)};")
        code.append("")
        
        code.append(f"void Draw_{varName}(int current_frame) {{")
        code.append("    // Find the appropriate keyframe or interpolate")
        code.append("    int prev_idx = 0;")
        code.append("    int next_idx = 0;")
        code.append("    float t = 0.0f;")
        code.append("")
        code.append("    // Find surrounding keyframes")
        code.append(f"    for (int i = 0; i < {varName}_keyframe_count; i++) {{")
        code.append(f"        if ({varName}_animation[i].frame <= current_frame)")
        code.append("            prev_idx = i;")
        code.append(f"        if ({varName}_animation[i].frame >= current_frame) {{")
        code.append("            next_idx = i;")
        code.append("            break;")
        code.append("        }")
        code.append("    }")
        code.append("")
        code.append("    // Calculate interpolation factor")
        code.append(f"    if (prev_idx != next_idx) {{")
        code.append(f"        t = float(current_frame - {varName}_animation[prev_idx].frame) / ")
        code.append(f"            float({varName}_animation[next_idx].frame - {varName}_animation[prev_idx].frame);")
        code.append("    }")
        code.append("")
        
        if self.useSmoothing:
            code.append("    // Apply cubic easing for smoother animation")
            code.append("    t = t * t * (3.0f - 2.0f * t);")
            code.append("")
        
        code.append("    // Interpolate values")
        code.append(f"    float x = ImLerp({varName}_animation[prev_idx].x, {varName}_animation[next_idx].x, t);")
        code.append(f"    float y = ImLerp({varName}_animation[prev_idx].y, {varName}_animation[next_idx].y, t);")
        code.append(f"    float rotation = ImLerp({varName}_animation[prev_idx].rotation, {varName}_animation[next_idx].rotation, t);")
        code.append(f"    float scale = ImLerp({varName}_animation[prev_idx].scale, {varName}_animation[next_idx].scale, t);")
        code.append(f"    float opacity = ImLerp({varName}_animation[prev_idx].opacity, {varName}_animation[next_idx].opacity, t);")
        code.append("")
        
        if self.itemType == "text":
            text = self.properties.get("text", "Text")
            code.append(f"    // Draw text")
            code.append(f"    ImGui::SetCursorPos(ImVec2(x, y));")
            code.append(f"    ImGui::PushStyleVar(ImGuiStyleVar_Alpha, opacity);")
            code.append(f"    if (rotation != 0.0f || scale != 1.0f) {{")
            code.append(f"        // Save current cursor position")
            code.append(f"        ImVec2 pos = ImGui::GetCursorScreenPos();")
            code.append(f"        ImDrawList* draw_list = ImGui::GetWindowDrawList();")
            code.append(f"        draw_list->PushTextureID(ImGui::GetFont()->ContainerAtlas->TexID);")
            code.append(f"        // Apply transformation")
            code.append(f"        draw_list->AddText(ImGui::GetFont(), ImGui::GetFontSize() * scale,")
            code.append(f"            pos, ImGui::GetColorU32(ImVec4(1,1,1,opacity)), \"{text}\");")
            code.append(f"        draw_list->PopTextureID();")
            code.append(f"    }} else {{")
            code.append(f"        ImGui::Text(\"{text}\");")
            code.append(f"    }}")
            code.append(f"    ImGui::PopStyleVar();")
        elif self.itemType in ["Rectangle", "Square"]:
            r, g, b, a = self.fillColor.getRgbF()
            code.append(f"    // Draw rectangle")
            code.append(f"    ImGui::SetCursorPos(ImVec2(x, y));")
            code.append(f"    ImDrawList* draw_list = ImGui::GetWindowDrawList();")
            code.append(f"    ImVec2 p_min = ImGui::GetCursorScreenPos();")
            w = self.properties.get("width", 100)
            h = self.properties.get("height", 100)
            code.append(f"    ImVec2 p_max = ImVec2(p_min.x + {w} * scale, p_min.y + {h} * scale);")
            code.append(f"    ImU32 col = ImGui::GetColorU32(ImVec4({r:.2f}f, {g:.2f}f, {b:.2f}f, {a:.2f}f * opacity));")
            code.append(f"    if (rotation != 0.0f) {{")
            code.append(f"        // Calculate center for rotation")
            code.append(f"        ImVec2 center = ImVec2((p_min.x + p_max.x) * 0.5f, (p_min.y + p_max.y) * 0.5f);")
            code.append(f"        // Calculate corners")
            code.append(f"        ImVec2 corners[4] = {{")
            code.append(f"            ImVec2(p_min.x, p_min.y),")
            code.append(f"            ImVec2(p_max.x, p_min.y),")
            code.append(f"            ImVec2(p_max.x, p_max.y),")
            code.append(f"            ImVec2(p_min.x, p_max.y)")
            code.append(f"        }};")
            code.append(f"        // Rotate corners")
            code.append(f"        float cos_r = cosf(rotation * 3.14159f / 180.0f);")
            code.append(f"        float sin_r = sinf(rotation * 3.14159f / 180.0f);")
            code.append(f"        for (int i = 0; i < 4; i++) {{")
            code.append(f"            ImVec2 temp = corners[i];")
            code.append(f"            corners[i].x = center.x + (temp.x - center.x) * cos_r - (temp.y - center.y) * sin_r;")
            code.append(f"            corners[i].y = center.y + (temp.x - center.x) * sin_r + (temp.y - center.y) * cos_r;")
            code.append(f"        }}")
            code.append(f"        draw_list->AddConvexPolyFilled(corners, 4, col);")
            code.append(f"    }} else {{")
            code.append(f"        draw_list->AddRectFilled(p_min, p_max, col);")
            code.append(f"    }}")
        elif self.itemType == "Circle":
            r, g, b, a = self.fillColor.getRgbF()
            code.append(f"    // Draw circle")
            code.append(f"    ImGui::SetCursorPos(ImVec2(x, y));")
            code.append(f"    ImDrawList* draw_list = ImGui::GetWindowDrawList();")
            code.append(f"    ImVec2 center = ImGui::GetCursorScreenPos();")
            radius = self.properties.get("radius", 40)
            code.append(f"    center.x += {radius} * scale;")
            code.append(f"    center.y += {radius} * scale;")
            code.append(f"    ImU32 col = ImGui::GetColorU32(ImVec4({r:.2f}f, {g:.2f}f, {b:.2f}f, {a:.2f}f * opacity));")
            code.append(f"    draw_list->AddCircleFilled(center, {radius} * scale, col);")
        else:
            r, g, b, a = self.fillColor.getRgbF()
            code.append(f"    // Draw shape")
            code.append(f"    ImGui::SetCursorPos(ImVec2(x, y));")
            code.append(f"    ImDrawList* draw_list = ImGui::GetWindowDrawList();")
            code.append(f"    ImVec2 center = ImGui::GetCursorScreenPos();")
            code.append(f"    center.x += 40 * scale;")
            code.append(f"    center.y += 40 * scale;")
            code.append(f"    ImU32 col = ImGui::GetColorU32(ImVec4({r:.2f}f, {g:.2f}f, {b:.2f}f, {a:.2f}f * opacity));")
            code.append(f"    float radius = 40.0f * scale;")
            code.append(f"    draw_list->AddCircleFilled(center, radius, col);")
        
        code.append("}")
        
        return "\n".join(code)
