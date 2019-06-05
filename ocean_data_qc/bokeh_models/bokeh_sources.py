# -*- coding: utf-8 -*-
#########################################################################
#    License, authors, contributors and copyright information at:       #
#    AUTHORS and LICENSE files at the root folder of this application   #
#########################################################################

import time
import numpy as np
import pandas as pd
from bokeh.util.logconfig import bokeh_logger as lg
from bokeh.models.sources import ColumnDataSource, CDSView
from bokeh.models.filters import IndexFilter
from bokeh.palettes import Reds3

from ocean_data_qc.env import Environment
from ocean_data_qc.constants import *
import ocean_data_qc.data_models.tools as tools


class BokehSources(Environment):
    env = Environment

    def __init__(self, **kwargs):
        lg.info('-- INIT BOKEH DATA')
        self.env.bk_sources = self

    def load_data(self):
        lg.info('-- LOAD DATA')
        self.env.f_handler.load_data()
        self._init_cds_df()
        self._init_bathymetric_map_data()
        self.env.stations = self.env.cruise_data.stations
        self.env.source = ColumnDataSource(self.env.cds_df)
        self._init_prof_ml_source()
        self._init_astk_src()
        self._init_all_flag_values()

    def _init_cds_df(self):
        ''' Create integer index on the dataframe
            The main DF has hashs strings as indices, so we need to create a new index
            TODO: Should I create a multilevel index???
        '''
        if self.env.cruise_data.df is None:
            self.env.cruise_data.load_file()  # for AQC files
        length = len(self.env.cruise_data.df.index)
        index = np.array(np.array(list(range(0,length))))
        self.env.cds_df = self.env.cruise_data.df.copy(deep=True)   # TODO: copy only the columns needed, not all of them??
        self.env.cds_df['INDEX'] = index                               # NOTE: the index will coincide with the row position
        self.env.cds_df = self.env.cds_df.set_index(['INDEX'])          #       so .iloc can be used in order to get the rows

    def _epsg4326_to_epsg3857(self, lon, lat):
        x = lon * 20037508.34 / 180
        y = np.log(np.tan((90 + lat) * np.pi / 360)) / (np.pi / 180) * 20037508.34 / 180
        return(x, y)

    def _init_bathymetric_map_data(self):
        x_wm, y_wm = self._epsg4326_to_epsg3857(
            self.env.cds_df.LONGITUDE.as_matrix(),
            self.env.cds_df.LATITUDE.as_matrix()
        )
        aux_df = pd.DataFrame(dict(
            X_WMTS=x_wm,
            Y_WMTS=y_wm,
            STNNBR=list(self.env.cds_df[STNNBR])
        ))
        aux_df.drop_duplicates(subset=STNNBR, keep='first', inplace=True)
        lg.info('>> AUX DF LEN: {}'.format(aux_df.index.size))
        new_index_column = list(range(aux_df.index.size))
        lg.info('>> AUX DF new_index_column: {}'.format(len(new_index_column)))
        aux_df = aux_df.assign(NEW_INDEX=new_index_column)
        aux_df.set_index(keys='NEW_INDEX', inplace=True)
        self.env.wmts_map_df = aux_df.copy(deep=True)
        self.env.wmts_map_source = ColumnDataSource(self.env.wmts_map_df)

    def _init_flag_views(self):
        '''
            The result should be something like this:

            self.env.views = {
                'TAB_NAME': {
                    0: view_object_0,
                    1: view_object_1,
                }
            }

            NOTE: self.env.all_flags and  self.env.tabs_flags_plots should be created beforehand
        '''
        lg.info('-- INIT FLAG VIEWS')
        # lg.warning('>> SELF.ENV.ALL_FLAGS: {}'.format(self.env.all_flags))
        # lg.warning('>> self.env.tabs_flags_plot: {}'.format(self.env.tabs_flags_plots))
        # lg.warning('>> self.env.f_handler.tab_list: {}'.format(self.env.f_handler.tab_list))
        # lg.info('>> self.env.source.data: {}'.format(self.env.source.data))

        # TODO: tabs with the same flag should share the views

        for tab in self.env.f_handler.tab_list:
            flag = tab + FLAG_END
            flags = {}
            for i, val in enumerate(self.env.source.data[flag]):
                flags.setdefault(int(val), []).append(i)

            flag_views = {}
            for key in list(self.env.all_flags.keys()):
                if key in flags:
                    view = CDSView(source=self.env.source, filters=[IndexFilter(flags[key])])
                else:  # there is no values
                    view = CDSView(source=self.env.source, filters=[IndexFilter([])])
                flag_views[key] = view
            self.env.flag_views[tab] = flag_views

        # lg.info('>> SELF.ENV.FLAG_VIEWS: {}'.format(self.env.flag_views))


    def _init_prof_circle_source(self):
        ''' Creates a CDS for the profile points. So the column names:
                NITRAT_SALTNY_5:
                    * NITRAT >> Tab where the plot is drawn
                    * SALTNY >> Column data
                    * 5      >> Station number: (0, 1, 2, 3, 4 or 5) for NPROF = 6
        '''
        lg.info('-- INIT PROF CIRCLES SOURCES')
        d = {}
        compound_cols = []
        # lg.info('>> TABS FLAGS PLOTS: {}'.format(self.env.tabs_flags_plots))
        graphs = self.env.f_handler.graphs_per_tab
        for tab in self.env.f_handler.tab_list:
            for graph in graphs[tab]:

            # for col in self.env.cds_df.columns.tolist():  # TODO: not all of them
                for i in range(NPROF):
                    compound_cols.append('{}_{}_{}'.format(tab, graph.x, i))
                    compound_cols.append('{}_{}_{}'.format(tab, graph.y, i))
        compound_cols = list(set(compound_cols))
        if compound_cols != []:
            d = dict.fromkeys(compound_cols, np.array([np.nan] * self.env.cds_df.index.size))
        self.env.pc_src = ColumnDataSource(d)

    def _init_prof_ml_source(self):
        ''' Multiline ColumnDataSource Initialization '''
        colors = []
        line_width = []
        init_ml_profs = []

        # VIEWS
        for i in range(NPROF - 1, -1, -1):
            if i == NPROF - 1:          # TODO: add this to the CDS
                colors.append(Reds3[0])
                line_width.append(2)
            else:
                colors.append(BLUES[i])
                line_width.append(2)
            init_ml_profs.append(np.array([np.nan]))

        # ML SOURCE
        init_source_dict = dict(colors=colors, line_width=line_width)
        for i in range(self.env.n_plots):
            init_source_dict['xs{}'.format(i)] = init_ml_profs
            init_source_dict['ys{}'.format(i)] = init_ml_profs
        self.env.ml_src = ColumnDataSource(data=init_source_dict)

    def _init_astk_src(self):
        lg.info('-- INIT ASTERISK SOURCE')
        d = {}
        compound_cols = []
        graphs = self.env.f_handler.graphs_per_tab
        for tab in self.env.f_handler.tab_list:
            for graph in graphs[tab]:
                compound_cols.append('{}_{}'.format(tab, graph.x))
                compound_cols.append('{}_{}'.format(tab, graph.y))
        compound_cols = list(set(compound_cols))
        if compound_cols != []:
            d = dict.fromkeys(compound_cols, [])
        self.env.astk_src = ColumnDataSource(d)

    def _init_all_flag_values(self):
        ''' Set all the possible flag values. Generates a dictionary like this:
            self.env.all_flags = {
                2: 'FLAG 2',
                3: 'FLAG 3',
                ...
            }
        '''
        cols = self.env.cruise_data.get_cols_by_type(['param_flag', 'qc_param_flag'])
        flag_vals = self.env.cds_df[cols].values.ravel('K')  # ravel('K') to flatten the multidimensional array
        flag_vals = flag_vals[~np.isnan(flag_vals)]          # remove nan
        flag_vals = np.unique(flag_vals)                     # select the unique values
        flag_vals = flag_vals.astype(np.int64)               # convert to integer
        flag_vals = flag_vals.tolist()                       # convert to python list

        # forcing the basic values
        # TODO: Create a flag form in order to set the flag values by hand
        if 2 not in flag_vals:
            flag_vals.append(2)
        if 3 not in flag_vals:
            flag_vals.append(3)
        if 4 not in flag_vals:
            flag_vals.append(4)
        flag_vals = sorted(flag_vals)

        for f in flag_vals:
            self.env.all_flags[f] = 'Flag {}'.format(f)
        if len(flag_vals)>len(CIRCLE_COLORS):
            for f in flag_vals:
                if f > 9:
                    CIRCLE_COLORS.update({f: CIRCLE_COLORS[9]})

    def _upd_prof_srcs(self, force_selection=False):
        ''' Selects the points of the profile line and update the multiline data source
            and asterisks and circles views to draw the whole profiles.
            This method should be the most efficient of the app
                @force_selection: a new partial selection should be done from scratch
        '''
        lg.info('-- UPDATE PROF SOURCES')

        # TODO: send signal to disable the rest of tabs
        self.env.bk_bridge.call_js({
            'object': 'bokeh.calls',
            'function': 'disable_tabs',
        })
        start = time.time()
        if self.env.cur_partial_stt_selection == [] or force_selection:
            self._set_partial_stt_selection()  # len(partial_stt_selection) <= NPROF

        astk_cds = self._upd_astk_src()
        self.env.astk_src.data = astk_cds.data

        p1 = time.time()

        ml_df, df_fs, stt_order = self._get_ml_df()
        ml_patches = self._get_ml_src_patches(ml_df)
        self.env.ml_src.patch(ml_patches)

        p2 = time.time()
        prof_df = self._upd_pc_srcs(df_fs, stt_order)
        p3 = time.time()
        pc_patches = self._get_pc_src_patches(prof_df)
        p4 = time.time()
        self.env.pc_src.patch(pc_patches)
        # self.env.pc_src.data = self.env.pc_src.from_df(prof_df)
        p5 = time.time()
        self.env.pc_src.selected.indices = self.env.selection

        p6 = time.time()
        lg.warning('>> PC SOURCES: {}, {}, {}, {}, SUM = {}'.format(
            round(p3 - p2, 2),
            round(p4 - p3, 2),
            round(p5 - p4, 2),
            round(p6 - p5, 2),
            sum([
                round(p3 - p2, 2),
                round(p4 - p3, 2),
                round(p5 - p4, 2),
                round(p6 - p5, 2)
            ])
        ))
        lg.info('>> TIME: ASTERISK: {} | ML: {} | PC: {} >> FULL ALGORITHM TIME: {}'.format(
            round(p1 - start, 2), round(p2 - p1, 2), round(p6 - p2, 2), round(p6 - start, 2)
        ))

    def _get_ml_src_patches(self, ml_df=None):
        lg.info('-- GET ML SRC PATCHES')
        ml_df.reset_index(drop=True, inplace=True)

        # ml_src_df_old
        ml_src_df_old = self.env.ml_src.to_df()
        del ml_src_df_old['colors']          # colors and line_width are set in the initialization
        del ml_src_df_old['line_width']
        ml_src_df_old = ml_src_df_old.applymap(
            lambda x: None if x == [] else np.array([np.nan])
        )
        ml_src_df_old = ml_src_df_old.stack().reset_index(level=0)
        s_old = ml_src_df_old.apply(lambda x: tuple(x), axis=1)
        d_old = s_old.groupby(s_old.index).apply(lambda x: x.tolist()).to_dict()

        # ml_src_df_new
        ml_src_df_new = ml_df.applymap(lambda x: None if x == [''] else x)  # this is a replace
        ml_src_df_new = ml_src_df_new.stack().reset_index(level=0)
        s_new = ml_src_df_new.apply(lambda x: tuple(x), axis=1)
        d_new = s_new.groupby(s_new.index).apply(lambda x: x.tolist()).to_dict()

        ml_patches = tools.merge(d_old, d_new)
        return ml_patches

    def _get_pc_src_patches(self, prof_df=None):
        ''' Basically this method make these steps:
                1. Get non-nan values positions to reset just them
                2. Mix these positions with the new values
                3. Reduce the number of slices by groups
                4. Send patch

                NOTE: How to patch NaN values: https://github.com/bokeh/bokeh/issues/7525
                      The indices must be int (Int64 throws error)
        '''
        lg.info('-- GET PC SRC PATCHES')
        # TODO: merge both dataframes in a different way, check if "merge", "join", or "assign" will work
        # pc_df = self.env.pc_src.to_df()  # get values and convert to NaN, mark them with some flag??
        # merged_df = pc_df.assign(**prof_df.to_dict())

        # prof_df.to_pickle('prof_df.pickle')
        # self.env.pc_src.to_df().to_pickle('pc_src_df_old.pickle')

        start = time.time()

        pc_src_df_old = self.env.pc_src.to_df()
        pc_src_d_old = {}
        for c in pc_src_df_old.columns:
            s = pc_src_df_old[pc_src_df_old[c].notnull()][c]
            if s.index.size > 0:
                pc_src_d_old[c] = list(zip(s.index, [np.nan] * s.index.size))

        # print('>> OLD SRC VALUES: {}'.format(pc_src_d_old.get('SILCAT_PRES_1', False)))

        pc_src_d_new = {}
        for c in prof_df.columns:
            s = prof_df[prof_df[c].notnull()][c]
            if s.index.size > 0:
                pc_src_d_new[c] = list(zip(s.index, s))

        # print('>> NEW SRC VALUES: {}'.format(pc_src_d_new.get('SILCAT_PRES_1', False)))

        if pc_src_d_old != {}:
            patches = tools.merge(pc_src_d_old, pc_src_d_new)
        else:
            patches = pc_src_d_new
        for key in patches.keys():
            patches[key] = tools.trans(dict(patches[key]))

        end = time.time()
        lg.warning('>> GET PC_SRC PATCHES: {}'.format(round(end - start, 2)))

        return patches

    def _get_ml_df(self):
        lg.info('-- GET ML DF')
        df_fs = None
        stt_order = []

        # TODO: only one tab >> plots in the current tab
            # self.env.tabs_flags_plots = {
            #     'NITRAT': {
            #         'flag': 'NITRAT_FLAG_W',       # default flag to mark in the dropdown
            #         'plots': [0, 1, 2, 3]          # plot list in order to create the gridplot
            #     },
            #     'SALNTY': {
            #         'flag': 'SALNTY_FLAG_W',
            #         'plots': [4, 5, 6]
            #     },

            #     # [...]
            # }

        n_cur_bk_plots = self.env.tabs_flags_plots[self.cur_tab]['plots']
        cur_bk_plots = []
        for n in n_cur_bk_plots:
            cur_bk_plots.append(self.env.bk_plots[n])
        lg.warning('>> N CUR BK PLOTS: {}'.format(n_cur_bk_plots))
        lg.warning('>> CUR BK PLOTS: {}'.format(cur_bk_plots))

        stts = self.env.cur_partial_stt_selection
        lg.warning('>> STTS: {}'.format(stts))

        if stts != []:
            ml_df = pd.DataFrame(index=stts, columns=[])
            df_fs = self.env.cds_df[self.env.cds_df[STNNBR].isin(stts)]

            d_ml_df = {}
            for bp in cur_bk_plots:
                df_p =  df_fs[df_fs[bp.x].notnull() & df_fs[bp.y].notnull()].sort_values([CTDPRS], ascending=[True])

                # FIXME: if one of the axis is CTDPRS then it gives an error here
                #       because the column is duplicated

                if self.env.plot_prof_invsbl_points is False:
                    df_p = df_p[df_p[bp.flag].isin(self.env.visible_flags)]

                if df_p.index.size >= 1:
                    d_ml_df.update({
                        'xs{}'.format(bp.n_plot): df_p.groupby(STNNBR).apply(lambda x: list(x[bp.x])),
                        'ys{}'.format(bp.n_plot): df_p.groupby(STNNBR).apply(lambda x: list(x[bp.y])),
                    })
                else:
                    d_ml_df.update(**{
                        'xs{}'.format(bp.n_plot): [[''] for x in stts],
                        'ys{}'.format(bp.n_plot): [[''] for x in stts],
                    })

            ml_df = ml_df.assign(**d_ml_df)
            if ml_df.index.size >= 1:
                stt_order = ml_df.index.drop(self.env.stt_to_select).tolist()
                stt_order.append(self.env.stt_to_select)  # at the end
                ml_df = ml_df.applymap(
                    lambda x: x if isinstance(x, list) else np.array([np.nan])  # np.nan > np.array([np.nan])
                )
            else:
                ml_df = self._reset_ml_src()
        else:
            ml_df = self._reset_ml_src()
        return ml_df, df_fs, stt_order

    def _set_partial_stt_selection(self):
        ''' Selects the first NPROF points with different stations
            in order to plot the profile lines
                @return list with non-duplicated stations
        '''
        lg.info('-- SET PARTIAL STT SELECTION')
        df = self.env.cds_df.filter([self.env.cur_flag])     # filter by flag column
        df = df.iloc[self.env.selection]                    # filter by selected points

        # if not self.env.plot_prof_invsbl_points:
        #     df = df[df[self.env.cur_flag].isin(self.env.visible_flags)]  # filter by visible points

        visible_selection = list(df.index.values)
        self.env.stt_to_select = None
        self.env.cur_partial_stt_selection = []
        if visible_selection != []:
            if self.env.sample_to_select is None:
                self.env.sample_to_select = visible_selection[0]
            self.env.stt_to_select = self.env.cds_df.iloc[[self.env.sample_to_select]][STNNBR].values[0]  # iloc or loc??? they coincide in this case I think
            self.env.cur_partial_stt_selection.append(self.env.stt_to_select)  # TODO: more than one station may be selected

            if self.env.plot_nearby_prof:
                if self.env.cur_nearby_prof is None:
                    self.env.bk_events.set_cur_nearby_prof()  # stt_to_select is already updated
                                                             # this should be run only when there is a new selection or sample change
                self.env.cur_partial_stt_selection.append(self.env.cur_nearby_prof)  # cur_nearby_prof is always different from stt_to_select
            else:
                # NPROF - 1 because I do not count the red profile >> why???
                i = 0
                while len(self.env.cur_partial_stt_selection) < (NPROF - 1) and i < len(visible_selection):
                    stt = self.env.cds_df.iloc[[visible_selection[i]]][STNNBR].values[0]
                    if stt not in self.env.cur_partial_stt_selection:
                        self.env.cur_partial_stt_selection.append(stt)
                    i += 1

        # lg.info('>> SAMPLE TO SELECT: {}'.format(self.env.sample_to_select))
        # lg.info('>> STT TO SELECT: {}'.format(self.env.stt_to_select))
        # lg.info('>> PARTIAL STT SELECTION: {}'.format(self.env.cur_partial_stt_selection))
        # lg.info('>> CUR NEARBY PROF: {}'.format(self.env.cur_nearby_prof))
        # lg.info('>> TOTAL SELECTION: {}'.format(self.env.selection))
        # lg.info('>> VISIBLE SELECTION (the first one is selected): {}'.format(visible_selection))

    def _upd_pc_srcs(self, df_fs=None, stt_order=[]):
        ''' Update profile circle sources. The self.env.pc_src is updated
            in order to mark the selected samples profiles over all the plots.

            @df_fs: DF with data only with the current stations to show
            @stt_order: selected stations, red color at the end of the list
        '''
        lg.info('-- UPDATE PROFILE CIRCLE SOURCES')
        start = time.time()
        prof_df = self._get_empty_prof_df()
        # tabs = self.env.f_handler.tab_list

        if df_fs is not None:
            stt_order_reversed = list(reversed(stt_order))
            d_temp = {}
            df_cur = df_fs.filter(self.env.cur_plotted_cols + [STNNBR])

            cur_cols_in_tab = self.env.f_handler.get_cols_in_tab(self.env.cur_tab)
            if self.env.plot_prof_invsbl_points is False:
                flag = self.env.tabs_flags_plots[self.env.cur_tab]['flag']
                df_cur = df_fs[df_fs[flag].isin(self.env.visible_flags)]

            i = NPROF - 1
            for stt in stt_order_reversed:
                df_stt = df_cur[df_cur[STNNBR] == stt]
                for col in cur_cols_in_tab:  # TODO: only for cols that appear in the current processed tab
                    df_aux = df_stt[col]
                    d_temp['{}_{}_{}'.format(self.env.cur_tab, col, i)] = df_aux
                i -= 1
            prof_df = prof_df.assign(**d_temp)
            # prof_df.dropna(how='all', inplace=True)   # just in case there are some NaN rows lefovers

        # NOTE: this translates the selection indices into positional indices
        #       bokeh with each ColumnDataSource uses a new index with consecutive integers [0, 1, 2, 3, ...]
        #       it doesn´t matter if you have a different index in the DF that you use to create the CDS

        # prof_sel = []
        # for i in self.env.selection:   # TODO: only selected points within profiles
        #     if i in prof_df.index:
        #         prof_sel.append(prof_df.index.get_loc(i))

        end = time.time()
        lg.warning('-- _upd_pc_srcs time: {}'.format(round(end - start, 2)))
        return prof_df

    def _get_empty_prof_df(self):
        ''' DF initialization with empty values '''

        lg.info('-- GET EMPTY PROF DF')
        compound_cols = []
        for tab in self.env.f_handler.tab_list:
            plot_indices = self.env.tabs_flags_plots[tab]['plots']
            aux_cols = []
            for pi in plot_indices:
                aux_cols.append(self.env.bk_plots[pi].x)
                aux_cols.append(self.env.bk_plots[pi].y)
            aux_cols = list(set(aux_cols))  # removes duplicates
            # lg.info('>> AUX COLS: {}'.format(aux_cols))
            for col in aux_cols:  # TODO: not all of them
                for n in range(NPROF):
                    compound_cols.append('{}_{}_{}'.format(tab, col, n))
        compound_cols.sort()

        d = {}
        if compound_cols != []:
            d = dict.fromkeys(compound_cols, np.array([np.nan] * self.env.cds_df.index.size))
        prof_df = pd.DataFrame(d)  # init empty columns
        prof_df['INDEX'] = self.env.cds_df.index
        prof_df = prof_df.set_index(['INDEX'])

        return prof_df

    def _upd_astk_src(self):
        ''' Creates a new CDS with the new asterisk source data (selected sample)
            If nothing is selected the CDS is reset.

            NOTE: Be careful with this method because the lists orders is very important
                  and dificult to follow
        '''
        lg.info('-- UPDATE ASTERISK SOURCE')
        if self.env.sample_to_select is not None:
            values = [np.nan] * (len(self.env.cur_plotted_cols) * len(self.env.f_handler.tab_list))   # values should have the same order than the CDS columns
            columns = []
            pos = 0
            for tab in self.env.f_handler.tab_list:
                for col in self.env.cur_plotted_cols:
                    columns.append('{}_{}'.format(tab, col))
                    if self.env.plot_prof_invsbl_points:  # then always visible
                        values[pos] = self.env.cds_df.loc[self.env.sample_to_select, col]
                    else:
                        flag = self.env.tabs_flags_plots[tab]['flag']
                        if self.env.cds_df.loc[self.env.sample_to_select, flag] in self.env.visible_flags:
                            values[pos] = self.env.cds_df.loc[self.env.sample_to_select, col]
                    pos += 1

            # lg.info('>> COLUMNS: {}'.format(columns))
            # lg.info('>> VALUES: {}'.format(values))
            df = pd.DataFrame(columns=columns)
            if any(not np.isnan(x) for x in values):
                df.loc[self.env.sample_to_select] = values
        else: # posibbly reset
            lg.info('>> RESETTING ASTERISK')
            column_names = list(self.env.astk_src.data.keys())
            if 'index' in column_names:
                column_names.remove('index')
            df = pd.DataFrame(columns=column_names)
        astk_cds = ColumnDataSource(df)
        return astk_cds

    def _reset_ml_src(self):
        n_plots = self.env.bk_plots_handler.current_n_plots
        columns = ['{}s{}'.format(a, i) for i in range(n_plots) for a in ['x', 'y']]
        columns.append('colors')
        columns.append('line_width')
        ml_df = pd.DataFrame(columns=columns)
        return ml_df
