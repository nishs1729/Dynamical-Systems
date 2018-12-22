from scipy.integrate import odeint
from scipy import *

import bqplot as bq
from ipywidgets import interact, interactive, Layout, Box, HBox, VBox, Label
import ipywidgets as ipyw
from IPython.display import display


class slider():
    cpalette = ['#EE224A', '#22AF4B', '#4CB5F5', '#FF5C00', 
                '#08B9A5', '#15AB00', '#881EE4', '#5C6BC0']
    
    def __init__(self, model):
        self.model = model
        self.lines = {}
        self.param = {}
        self.cb = {}
        self.colors = {}
        
        self._solve()
        self._curveColors()
        self._plot()
        
        
    def _curveColors(self):
        for i,v in enumerate(self.model.label):
            self.colors.update({v: self.cpalette[i]})
        
    def _solve(self):
        sol = odeint(self.model.dXdt, self.model.X0, self.model.T)
        
        self.sol = {}
        for i,var in enumerate(self.model.label):
            self.sol.update({var: sol[:,i]})
    
    def _getFig(self):
        for v in self.model.label:
            x_sc = bq.LinearScale()
            y_sc = bq.LinearScale()

            x_ax = bq.Axis(label='Time', scale=x_sc, tick_format='0.0f', color='black', grid_lines='solid', grid_color='#ddd')
            y_ax = bq.Axis(label=v,      scale=y_sc, tick_format='0.2f', color='black', grid_lines='solid', grid_color='#ddd', orientation='vertical')

            # Generate a line (but does not plot it)
            l = bq.Lines(x=self.model.T, y=self.sol[v], colors=[self.colors[v]],
                              scales={'x': x_sc, 'y': y_sc})
        
            self.lines.update({v: l})
          
        fig = bq.Figure(axes=[x_ax, y_ax], marks=self.lines.values(),
                       fig_margin={'top':10, 'bottom':0, 'left':60, 'right':10},
                       max_aspect_ratio=3, min_aspect_ratio=2.5)
        fig.layout.width = '100%'
        return fig
        
    def _plot(self):
        self._solve()
        fig = self._getFig()
        
        display(fig)
        
    def _updateFig(self):        
        self._solve()
        for v in self.model.label:
            self.lines[v].y = self.sol[v]
    
    ### Parameter handling
    def _paramUpdate(self, change):
        self.model.p[change['owner'].description] = change['new']
        self._updateFig()
            
    def paramSlider(self):
        for k,v in self.model.p.items():
            crude = ipyw.IntSlider(
                min = -5, max = 10,
                description=k,
                value = floor(log10(v)), 
                continuous_update = False
            )

            fine = ipyw.FloatSlider(
                min = 10**floor(log10(v)),
                max = 10**(floor(log10(v))+1),
                description=k, 
                value = v,
                continuous_update = False
            )
            
            #txt = ipyw.FloatText(value=v, description=k, layout=Layout(width='80px'))
        
            #ipyw.jslink((fine, 'value'), (txt, 'value'))
            crude.observe(self._updateRange, names='value')
            fine.observe(self._paramUpdate,  names='value')
        
            p = [crude, fine]#, txt]
            self.param.update({k: p})
        
        box_layout = Layout(display='flex-start',
                    flex_flow='row',
                    align_items='flex-start',
                    align_content='flex-start',
                    width='100%')
        
        for k, v in self.param.items():
            box = Box(children=v, layout=box_layout)
            display(box, layout=Layout(align_items='flex-start'))
            
            
    def _updateRange(self, c):
        k = c['owner'].description
        try:
            self.param[k][1].max = 10**(c['new']+1)
            self.param[k][1].min = 10**c['new']
        except:
            self.param[k][1].min = 10**c['new']
            self.param[k][1].max = 10**(c['new']+1)
        self.param[k][1].value = self.param[k][1].min
        self.param[k][1].step = 1 if c['new']>0 else 10**(c['new']-1)
        
    ### Toggle curve display
    def _toggleCurve(self, b):
        v = not self.lines[b.description].visible
        if self.lines[b.description].visible:
            self.cb[b.description].style.button_color = '#ddd'
            self.lines[b.description].visible = v
        else:
            self.cb[b.description].style.button_color = self.colors[b.description]
            self.lines[b.description].visible = v
        
        
    def _getToggleButton(self, v):
        cb = ipyw.Button(
            value = self.lines[v].visible,
            description = v,
            style = ipyw.ButtonStyle(button_color=self.colors[v]),
            layout = Layout(width='100px')
        )
        return cb
        
    def toggleButton(self):
        for v in self.model.label:
            self.cb.update({v: self._getToggleButton(v)})
            
        display(VBox(self.cb.values()))
        
        for cb in self.cb.values():
            cb.on_click(self._toggleCurve)