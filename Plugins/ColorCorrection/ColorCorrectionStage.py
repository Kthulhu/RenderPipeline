
from __future__ import division

from .. import *
from panda3d.core import SamplerState, Texture

class ColorCorrectionStage(RenderStage):

    required_pipes = ["ShadedScene"]
    required_inputs = ["TimeOfDay", "mainCam", "mainRender", "cameraPosition", "frameDelta"]

    def __init__(self, pipeline):
        RenderStage.__init__(self, "ColorCorrectionStage", pipeline)
        self._use_auto_exposure = True

    def set_use_auto_exposure(self, flag):
        self._use_auto_exposure = flag

    def create(self):

        if self._use_auto_exposure:
            self._target_lum = self._create_target("GenerateLuminance")
            self._target_lum.set_quarter_resolution()
            self._target_lum.add_color_texture(bits=16)
            self._target_lum.prepare_offscreen_buffer()

            wsize_x = (Globals.base.win.get_x_size() + 3) // 4
            wsize_y = (Globals.base.win.get_y_size() + 3) // 4

            self._mip_targets = []
            last_tex = self._target_lum["color"]
            while wsize_x >= 4 or wsize_y >= 4:
                wsize_x = (wsize_x+3) // 4
                wsize_y = (wsize_y+3) // 4

                mip_target = self._create_target("DownscaleLum-" + str(wsize_x))
                mip_target.add_color_texture(bits=16)
                mip_target.set_size(wsize_x, wsize_y)
                mip_target.prepare_offscreen_buffer()
                mip_target.set_shader_input("SourceTex", last_tex)
                self._mip_targets.append(mip_target)
                last_tex = mip_target["color"]

            self._tex_exposure = Image.create_buffer("ExposureStorage", 1,
                Texture.T_float, Texture.F_rgba16)

            self._target_analyze = self._create_target("AnalyzeBrightness")
            self._target_analyze.set_size(1, 1)
            self._target_analyze.add_color_texture()
            self._target_analyze.prepare_offscreen_buffer()

            self._target_analyze.set_shader_input("ExposureStorage", self._tex_exposure.get_texture())
            self._target_analyze.set_shader_input("DownscaledTex", last_tex)
        
        self._target = self._create_target("ColorCorrectionStage")
        self._target.prepare_offscreen_buffer()
        self._target.make_main_target()

        if self._use_auto_exposure:
            self._target.set_shader_input("ExposureTex", self._tex_exposure.get_texture())

    def set_shaders(self):
        self._target.set_shader(self.load_plugin_shader("CorrectColor.frag.glsl"))

        if self._use_auto_exposure:
            self._target_lum.set_shader(self.load_plugin_shader("GenerateLuminance.frag.glsl"))
            self._target_analyze.set_shader(self.load_plugin_shader("AnalyzeBrightness.frag.glsl"))
            mip_shader = self.load_plugin_shader("DownscaleLuminance.frag.glsl")
            for target in self._mip_targets:
                target.set_shader(mip_shader)

    def resize(self):
        RenderStage.resize(self)
        self.debug("Resizing pass")

    def cleanup(self):
        RenderStage.cleanup(self)
        self.debug("Cleanup pass")