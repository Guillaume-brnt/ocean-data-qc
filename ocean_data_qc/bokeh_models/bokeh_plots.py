# -*- coding: utf-8 -*-
#########################################################################
#    License, authors, contributors and copyright information at:       #
#    AUTHORS and LICENSE files at the root folder of this application   #
#########################################################################

import numpy as np
from copy import deepcopy
from os import path
from bokeh.plotting import figure
from bokeh.models import CustomAction
from bokeh.models.sources import ColumnDataSource
from bokeh.models.filters import GroupFilter, BooleanFilter, IndexFilter
from bokeh.events import Reset, DoubleTap
from bokeh.models.renderers import GlyphRenderer
from bokeh.models.callbacks import CustomJS
from bokeh.models.glyphs import Line
from bokeh.models.markers import Scatter
from bokeh.palettes import Reds3
from bokeh.models.tools import (
    PanTool, BoxZoomTool, BoxSelectTool, WheelZoomTool,
    LassoSelectTool, CrosshairTool, TapTool, SaveTool, ResetTool,
    HoverTool
)
from bokeh.io import curdoc
from bokeh.util.logconfig import bokeh_logger as lg

from ocean_data_qc.env import Environment
from ocean_data_qc.constants import *


class BokehPlots(Environment):
    env = Environment

    def __init__(self, **kwargs):
        self.env.doc = curdoc()     # TODO: replace bk with env

        if 'x' in kwargs:
            self.x = kwargs['x']
        if 'y' in kwargs:
            self.y = kwargs['y']
        if 'title' in kwargs:
            self.title = kwargs['title']
        if 'n_plot' in kwargs:
            self.n_plot = kwargs['n_plot']
        if 'tab' in kwargs:
            self.tab = kwargs['tab']

        self.plot = None            # plot initialization, should be this a list of plots? or use this class for each plot?
        self.circles = []
        self.asterisk = None
        self.astk_cds = None
        self.lasso_select = None

        self._init_figure()
        self._init_color_circles()
        self._init_profile_lines()
        self._init_profile_lines_circles()
        self._init_asterisk()
        self._set_tools()
        self._set_events()

    def _init_figure(self):
        title = None
        if self.env.show_titles:
            title = self.title
        self.plot = figure(
            # name='silcat_vs_nitrat',     # TODO: build a unique name here?
            # width=600,                   # NOTE: the size is given in the gridplot
            # height=600,
            x_range=self.env.ranges[self.tab][self.x]['x_range'],
            y_range=self.env.ranges[self.tab][self.y]['y_range'],
            x_axis_label=self.x,
            y_axis_label=self.y,
            toolbar_location=None,
            tools='',
            title=title,
            output_backend=OUTPUT_BACKEND,

            lod_threshold=1,               # downsampling enabled when the glyph has more than 3000 samples

            border_fill_color='whitesmoke',   # TODO: this should be declared on the yaml file
            background_fill_color='whitesmoke',
        )
        self.plot.yaxis.axis_label_text_font_style = 'normal'
        self.plot.xaxis.axis_label_text_font_style = 'normal'

    def _init_color_circles(self):
        ''' Plot different circles depending on their flag
            All the flags should be plotted in all the plots,
            even if they do not have the right flag (self.env.all_flags)
        '''
        for key in self.env.all_flags:  # TODO: set some order (overlapping layers)
            # TODO: Waiting for the GroupFilter by numeric value https://github.com/bokeh/bokeh/issues/7524

            c = self.plot.scatter(
                x=self.x,
                y=self.y,
                size=4,
                line_color=None,
                fill_color=CIRCLE_COLORS[key],
                # fill_alpha=0.6,         # to see overlapping points??
                source=self.env.source,
                view=self.env.flag_views[self.tab][key],

                nonselection_line_color=None,
                nonselection_fill_color=CIRCLE_COLORS[key],
                nonselection_fill_alpha=1.0,
            )
            c.selection_glyph = Scatter(
                line_color=Reds3[0],
                line_alpha=1.0,
                fill_color='yellow',
            )
            c.tags = ['GR_FLAG_{}'.format(key), 'GR_FLAG']
            self.circles.append(c)

    def _init_profile_lines(self):
        ''' This is just a initialization of the Line GlyphRenderers.

            If some selected point are on the same profile, only one should be drawn

            Note: the line profiles cannot be plotted with CDSViews because if the indexes are
                  not consecutive then the line is not going to be only one line.
        '''
        self.ml_prof_line = self.plot.multi_line(
            xs='xs{}'.format(self.n_plot),
            ys='ys{}'.format(self.n_plot),
            source=self.env.ml_src,
            color='colors',
            line_cap='round',
            line_join='round',
            line_width='line_width',
        )

    def _init_profile_lines_circles(self):
        ''' This method renders the profile line vertexes (circles).
            Two glyphs are plotted:
                * Selected points
                * Non-selected points
        '''
        self.env.profile_colors = [BLUES[i] for i in range(NPROF - 1)]
        self.env.profile_colors.reverse()
        self.env.profile_colors = self.env.profile_colors + [RED]
        # profile colors = [..., light blue, blue, dark blue, red]
        for i in range(NPROF):
            color = self.env.profile_colors[i]
            c = self.plot.scatter(
                x='{}_{}_{}'.format(self.tab, self.x, i),
                y='{}_{}_{}'.format(self.tab, self.y, i),
                line_color=color,
                fill_color=color,
                size=4,             # this attr is common for the selection and non-selection glyph
                source=self.env.pc_src,

                nonselection_line_color=color,
                nonselection_fill_color=color,
                nonselection_line_alpha=1.0,
                nonselection_fill_alpha=1.0
            )
            c.selection_glyph = Scatter(
                line_color=RED,
                fill_color='yellow',
                line_alpha=1.0,
                fill_alpha=1.0
            )

    def _init_asterisk(self):
        ''' The asterisk is the mark for the current selected sample
                * self.asterisk - red asterisk on the background
                * self.aux_asterisk_asterisk - marked asterisk
                * self.aux_asteris_circle - center asterisk marked
        '''
        self.asterisk = self.plot.scatter(
            marker='asterisk',
            x='{}_{}'.format(self.tab, self.x),
            y='{}_{}'.format(self.tab, self.y),
            size=20,
            line_color=Reds3[0],
            line_width=3,
            source=self.env.astk_src,

            nonselection_line_color=None,       # NOTE: The following object is to avoid a shadow for a
            nonselection_fill_color=None,       #       few ms when a new selection is made
            nonselection_line_alpha=0.0,
            nonselection_fill_alpha=0.0
        )

        self.aux_asterisk = self.plot.scatter(
            marker='asterisk',
            x='{}_{}'.format(self.tab, self.x),
            y='{}_{}'.format(self.tab, self.y),
            size=17,
            line_color='yellow',
            line_width=1,
            source=self.env.astk_src,

            nonselection_line_color=None,
            nonselection_fill_color=None,
            nonselection_line_alpha=0.0,
            nonselection_fill_alpha=0.0
        )

        self.aux_asterisk_circle = self.plot.scatter(
            x='{}_{}'.format(self.tab, self.x),
            y='{}_{}'.format(self.tab, self.y),
            size=3,
            fill_color='yellow',
            line_width=None,
            line_color='yellow',
            source=self.env.astk_src,

            nonselection_line_color=None,
            nonselection_fill_color=None,
            nonselection_line_alpha=0.0,
            nonselection_fill_alpha=0.0
        )

    @property
    def flag(self):
        return self.env.tabs_flags_plots[self.tab]['flag']

    def _reset_plot(self, event):
        ''' This method should be assigned to all the plots to reset the zoom level and location
                * Hides all the Line GlyphRenderers on the plot.
                * The selection is also removed
                * The flag visibility is reset

            NOTE: this is run once per plot in each tab, but actually we need to run it only once
        '''
        lg.info('-- RESET PLOT: {}'.format(self.n_plot))
        n = self.env.tabs_flags_plots[self.tab]['plots'][0]  # first plot in the current tab
        if self.n_plot == n:
            self.env.reset_selection = True  # this does not work anymore
            self.env.selection = []
            self.env.source.selected.indices = []
            self.env.cur_partial_stt_selection = []  # in order to triger the partial selection method
            self.env.dt_manual_update = False
            self.env.bk_table.update_dt_source()
            self.env.dt_manual_update = True
            self.env.map_selection = []
            self.env.wmts_map_source.selected.indices = []
            self.env.bk_flags.reset_all_flags()

    def _double_tap_event(self, event):
        ''' This could be useful to change the axis variables
            or some other plot attributes on the fly
        '''
        lg.info('-- DOUBLE TAP EVENT, AXIS: {} | {}'.format(self.x, self.y))

    def _set_events(self):
        self.plot.on_event(DoubleTap, self._double_tap_event)
        self.plot.on_event(Reset, self._reset_plot)

    def _set_tools(self):
        wheel_zoom = WheelZoomTool()
        pan = PanTool()
        box_zoom = BoxZoomTool()
        box_select = BoxSelectTool()
        crosshair = CrosshairTool()
        tap = TapTool()
        save = SaveTool()
        reset = ResetTool()
        self.lasso_select = LassoSelectTool(
            renderers=self.circles,          # default = all available renderers
            select_every_mousemove=False,    # to enhance performance
        )
        hover = self._get_hover_tool()
        self.tools = (
            pan, box_zoom, self.lasso_select, box_select,
            crosshair, save, reset, tap, wheel_zoom
        )
        self.plot.add_tools(*self.tools)

    def _get_hover_tool(self):
        tooltips = '''
            <style>
                .bk-tooltip>div:not(:nth-child(-n+5)) {{
                    display:none;
                }}

                /* .bk-tooltip-custom + .bk-tooltip-custom {{
                    display: none;  sometimes everything is hidden with this
                }} */

                .bk-tooltip>div {{
                    background-color: #dff0d8;
                    padding: 5px;
                }}
            </style>

            <b>INDEX: </b> @INDEX <br>
            <b>{x}: </b> @{x} <br>
            <b>{x}_FLAG_W: </b> @{x}_FLAG_W <br>
            <b>{y}: </b> @{y} <br>
            <b>{y}_FLAG_W: </b> @{y}_FLAG_W <br>
        '''.format(x=self.x, y=self.y)

        hover = HoverTool(                  # TODO: try to make this toggleable
            renderers=self.circles,
            toggleable=True,
            mode='mouse',
            tooltips=tooltips,
        )
        return hover

    def add_deselect_tool(self):
        ''' This tool should be added only once per tab '''
        js_code = """
            window.top.postMessage({
                'signal': 'deselect-tool',
            }, '*');                        // to main_renderer.js
        """
        deselect_tool = CustomAction(  # I took this from ResetTool that inherits from CustomAction
            icon=path.join(IMG, 'deselect.png'),
            callback=CustomJS(code=js_code, args=dict(source=self.env.source, reset_selection=self.env.reset_selection)),
            action_tooltip='Reset Selection'
        )
        self.plot.add_tools(deselect_tool)  # reset is needed?
