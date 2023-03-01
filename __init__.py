bl_info = {
    "name": "Text List",
    "author": "tintwotin",
    "version": (1, 0),
    "blender": (2, 3, 0),
    "location": "Sequencer > Side Bar > Text List Tab",
    "description": "Displays a list of all Text List in the VSE and allows editing of their text.",
    "warning": "",
    "doc_url": "",
    "category": "Sequencer",
}

import bpy


def get_strip_by_name(name):
    for strip in bpy.context.scene.sequence_editor.sequences:
        if strip.name == name:
            return strip
    return None  # Return None if the strip is not found


def update_text(self, context):
    for strip in bpy.context.scene.sequence_editor.sequences:
        if strip.type == "TEXT" and strip.name == self.name:
            # Update the text of the text strip
            strip.text = self.text
            break
        strip_name = self.name
        strip = get_strip_by_name(strip_name)
        if strip:
            # Deselect all strips.
            for seq in context.scene.sequence_editor.sequences_all:
                seq.select = False
            bpy.context.scene.sequence_editor.active_strip = strip
            strip.select = True

            # Set the current frame to the start frame of the active strip
            bpy.context.scene.frame_set(int(strip.frame_start))


# def update_name(self, context):
#    for strip in bpy.context.scene.sequence_editor.sequences:
#        if strip.type == 'TEXT' and strip.text == self.text:
#            strip.name = self.name
#            break


# Define a custom property group to hold the text strip name and text
class TextStripItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    text: bpy.props.StringProperty(update=update_text)


# Define a UIList for the text strip items
class TEXT_UL_List(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        # split = layout.split(factor=0.8)
        layout.prop(item, "text", text="")
        # split.prop(item, "name", text="", emboss=False)


# Define an operator to refresh the list
class TEXT_OT_refresh_list(bpy.types.Operator):
    bl_idname = "text.refresh_list"
    bl_label = "Refresh List"

    def execute(self, context):
        active = context.scene.sequence_editor.active_strip
        # Clear the list
        context.scene.text_strip_items.clear()

        # Get a list of all Text List in the VSE
        text_strips = [
            strip
            for strip in bpy.context.scene.sequence_editor.sequences
            if strip.type == "TEXT"
        ]

        # Sort the Text List based on their start times in the timeline
        text_strips.sort(key=lambda strip: strip.frame_start)

        # Iterate through the sorted Text List and add them to the list
        for strip in text_strips:
            item = context.scene.text_strip_items.add()
            item.name = strip.name
            item.text = strip.text
        # Select the active strip in the UI list
        for seq in context.scene.sequence_editor.sequences_all:
            seq.select = False
        bpy.context.scene.sequence_editor.active_strip = strip
        strip.select = True
        for i, item in enumerate(context.scene.text_strip_items):
            if (
                context.scene.sequence_editor.active_strip
                and item.name == context.scene.sequence_editor.active_strip.name
            ):
                context.scene.text_strip_items_index = i - 1
                break
        return {"FINISHED"}


# class TEXT_OT_select_next(bpy.types.Operator):
#    bl_idname = "text.select_next"
#    bl_label = "Select Next"

#    def execute(self, context):
#        current_index = context.scene.text_strip_items_index
#        max_index = len(context.scene.text_strip_items) - 1

#        if current_index < max_index:
#            context.scene.text_strip_items_index += 1
#            update_text(self, context)

#        return {'FINISHED'}


# class TEXT_OT_select_previous(bpy.types.Operator):
#    bl_idname = "text.select_previous"
#    bl_label = "Select Previous"

#    def execute(self, context):
#        current_index = context.scene.text_strip_items_index
#        print(current_index)
#        if current_index > 0:
#            context.scene.text_strip_items_index -= 1
#            update_text(self, context)

#        return {'FINISHED'}


# Define the panel to hold the UIList and the refresh button
class TEXT_PT_panel(bpy.types.Panel):
    bl_idname = "TEXT_PT_panel"
    bl_label = "Text List"
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Text List"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column()
        col.template_list(
            "TEXT_UL_List",
            "",
            context.scene,
            "text_strip_items",
            context.scene,
            "text_strip_items_index",
            rows=5,
        )

        # col = row.column(align=True)
        col.operator("text.refresh_list", text="Refresh", icon="FILE_REFRESH")
        # col.operator("text.select_next", text="", icon="TRIA_UP")
        # col.operator("text.select_previous", text="", icon="TRIA_DOWN")


# Register the classes
def register():
    bpy.utils.register_class(TextStripItem)
    bpy.utils.register_class(TEXT_UL_List)
    bpy.utils.register_class(TEXT_OT_refresh_list)
    # bpy.utils.register_class(TEXT_OT_select_next)
    # bpy.utils.register_class(TEXT_OT_select_previous)
    bpy.utils.register_class(TEXT_PT_panel)

    bpy.types.Scene.text_strip_items = bpy.props.CollectionProperty(type=TextStripItem)
    bpy.types.Scene.text_strip_items_index = bpy.props.IntProperty()


# Unregister the classes
def unregister():
    bpy.utils.unregister_class(TextStripItem)
    bpy.utils.unregister_class(TEXT_UL_List)
    bpy.utils.unregister_class(TEXT_OT_refresh_list)
    # bpy.utils.unregister_class(TEXT_OT_select_next)
    # bpy.utils.unregister_class(TEXT_OT_select_previous)
    bpy.utils.unregister_class(TEXT_PT_panel)

    del bpy.types.Scene.text_strip_items
    del bpy.types.Scene.text_strip_items_index


# Register the addon when this script is run
if __name__ == "__main__":
    register()
