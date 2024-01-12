import modules.scripts as scripts
import gradio as gr
import os
from modules import shared
from aspect_ratios import aspect_ratios as aratio
from modules.ui_components import ToolButton

class CMButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)
        self.ar = ar

    def apply(self, w, h):
        separate_w_h = self.ar.split('/')
        # if self.ar > 1.0:  # fix height, change width
        #     w = self.ar * h
        # elif self.ar < 1.0:  # fix width, change height
        #     h = w / self.ar
        # else:  # set minimum dimension to both
        #     min_dim = min([w, h])
        #     w, h = min_dim, min_dim

        return list(map(int, separate_w_h))

    def reset(self, w, h):
        return [self.res, self.res]

class CivitaiModelsScript(scripts.Script):
    # Extension title in menu UI
    def title(self):
        return "Civitai Models"

    # Decide to show menu in txt2img or img2img
    # - in "txt2img" -> is_img2img is `False`
    # - in "img2img" -> is_img2img is `True`
    #
    # below code always show extension menu
    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
            gr.HTML(label="Aspect ratio", value="Aspect ratio", show_label=True)
            with gr.Row(
                    elem_id=f'{"img" if is_img2img else "txt"}2img_row_aspect_ratio'
            ):
                btns = [
                    CMButton(ar=ar, value=label, elem_classes=['cm_aspect_ratio'])
                    for ar, label in aratio.items()
                ]
                # with contextlib.suppress(AttributeError):
                for b in btns:
                    if is_img2img:
                        resolution = [self.i2i_w, self.i2i_h]
                    else:
                        resolution = [self.t2i_w, self.t2i_h]

                    b.click(
                        b.apply,
                        inputs=resolution,
                        outputs=resolution,
                    )

    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_width":
            self.t2i_w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.t2i_h = component

        if kwargs.get("elem_id") == "img2img_width":
            self.i2i_w = component
        if kwargs.get("elem_id") == "img2img_height":
            self.i2i_h = component

        if kwargs.get("elem_id") == "img2img_image":
            self.image = [component]
        if kwargs.get("elem_id") == "img2img_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img2maskimg":
            self.image.append(component)
        if kwargs.get("elem_id") == "inpaint_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img_inpaint_base":
            self.image.append(component)