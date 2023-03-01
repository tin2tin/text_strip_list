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
        strip = get_strip_by_name(self.name)
        if strip:
            # Deselect all strips.
            for seq in context.scene.sequence_editor.sequences_all:
                seq.select = False
            bpy.context.scene.sequence_editor.active_strip = strip
            strip.select = True

            # Set the current frame to the start frame of the active strip
            bpy.context.scene.frame_set(int(strip.frame_start))


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
        layout.prop(item, "text", text="", emboss=False)
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
        # Select only the active strip in the UI list
        for seq in context.scene.sequence_editor.sequences_all:
            seq.select = False
        if active:
            context.scene.sequence_editor.active_strip = active
            active.select = True
            # Set the current frame to the start frame of the active strip
            bpy.context.scene.frame_set(int(active.frame_start))
        return {"FINISHED"}


class TEXT_OT_add_strip(bpy.types.Operator):
    """Add a new text strip after the position of the current selected list item"""

    bl_idname = "text.add_strip"
    bl_label = "Add Text Strip"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        text_strips = scene.sequence_editor.sequences_all

        # Get the selected text strip from the UI list
        index = scene.text_strip_items_index
        strip_name = context.scene.text_strip_items[index].name
        strip = get_strip_by_name(strip_name)

        # Add a new text strip after the selected strip
        strips = scene.sequence_editor.sequences
        new_strip = strips.new_effect(
            name="",
            type="TEXT",
            channel=strip.channel,
            frame_start=strip.frame_final_start + strip.frame_final_duration,
            frame_end=strip.frame_final_start + (2 * strip.frame_final_duration),
        )

        # Copy the settings
        if strip and new_strip:
            new_strip.text = ""
            new_strip.font_size = strip.font_size
            new_strip.font = strip.font
            new_strip.color = strip.color
            new_strip.use_shadow = strip.use_shadow
            new_strip.blend_type = strip.blend_type
            new_strip.use_bold = strip.use_bold
            new_strip.use_italic = strip.use_italic
            new_strip.shadow_color = strip.shadow_color
            new_strip.box_margin = strip.box_margin
            new_strip.location = strip.location
            new_strip.align_x = strip.align_x
            new_strip.align_y = strip.align_y
            context.scene.sequence_editor.active_strip = new_strip
        # Refresh the UIList
        bpy.ops.text.refresh_list()

        # Select the new item in the UIList
        context.scene.text_strip_items_index = index + 1

        return {"FINISHED"}


class TEXT_OT_delete_strip(bpy.types.Operator):
    bl_idname = "text.delete_strip"
    bl_label = "Delete Strip"

    @classmethod
    def poll(cls, context):
        return context.scene.sequence_editor is not None

    def execute(self, context):
        scene = context.scene
        seq_editor = scene.sequence_editor

        # Get the selected text strip from the UI list
        index = scene.text_strip_items_index
        strip_name = scene.text_strip_items[index].name
        strip = get_strip_by_name(strip_name)
        if strip:
            # Deselect all strips
            for seq in context.scene.sequence_editor.sequences_all:
                seq.select = False
            # Delete the strip
            strip.select = True
            bpy.ops.sequencer.delete()

            # Remove the UI list item
            scene.text_strip_items.remove(index)
        return {"FINISHED"}


class TEXT_OT_select_next(bpy.types.Operator):
    bl_idname = "text.select_next"
    bl_label = "Select Next"

    def execute(self, context):
        current_index = context.scene.text_strip_items_index
        max_index = len(context.scene.text_strip_items) - 1

        if current_index < max_index:
            context.scene.text_strip_items_index += 1
            update_text(self, context)
        return {"FINISHED"}


class TEXT_OT_select_previous(bpy.types.Operator):
    bl_idname = "text.select_previous"
    bl_label = "Select Previous"

    def execute(self, context):
        current_index = context.scene.text_strip_items_index
        if current_index > 0:
            context.scene.text_strip_items_index -= 1
            update_text(self, context)
        return {"FINISHED"}


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

        row = row.column(align=True)
        row.operator("text.refresh_list", text="", icon="FILE_REFRESH")
        row.operator("text.add_strip", text="", icon="ADD", emboss=True)  # .index(item)
        row.operator(
            "text.delete_strip", text="", icon="REMOVE", emboss=True
        )  # .index(item)
        row.operator("text.select_previous", text="", icon="TRIA_UP")
        row.operator("text.select_next", text="", icon="TRIA_DOWN")


classes = [
    TextStripItem,
    TEXT_UL_List,
    TEXT_OT_refresh_list,
    TEXT_OT_add_strip,
    TEXT_OT_delete_strip,
    TEXT_OT_select_next,
    TEXT_OT_select_previous,
    TEXT_PT_panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.text_strip_items = bpy.props.CollectionProperty(type=TextStripItem)
    bpy.types.Scene.text_strip_items_index = bpy.props.IntProperty()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.text_strip_items
    del bpy.types.Scene.text_strip_items_index

    del bpy.types.Scene.text_strip_items
    del bpy.types.Scene.text_strip_items_index


# Register the addon when this script is run
if __name__ == "__main__":
    register()
