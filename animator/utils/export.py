def exportImguiCode(animatedItems):
    code = []
    code.append("// ImGui Animation Code (Make this a header sir.)")
    code.append("// Generated by PotatoIsCool's ImGui Animator")
    code.append("")
    code.append("// Make sure you have the imgui header file imported pretty please")
    code.append("#include \"imgui.h\"") # Make sure you have the imgui header btw
    code.append("")
    code.append("inline float ImLerp(float a, float b, float t) { return a + (b - a) * t; }")
    code.append("")
    
    for animatedItem in animatedItems:
        code.append(animatedItem.toImguiCode())
        code.append("")
    
    code.append("// Here is the main drawing function. You can call this in your render loop most of the time")
    code.append("void DrawAnimation(int current_frame) {")
    for i, animatedItem in enumerate(animatedItems):
        varName = animatedItem.name.lower().replace(" ", "_")
        code.append(f"    Draw_{varName}(current_frame);")
    code.append("}")
    
    return "\n".join(code)
