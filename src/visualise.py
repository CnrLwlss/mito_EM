import pandas as pd
pd.set_option('display.max_columns', None)
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import webbrowser
import numpy as np

ddir = "../data"
fnames = os.listdir(ddir)
fdict = {''.join(filter(str.isdigit, x)):os.path.join(ddir,x) for x in fnames if "Conor" in x}

dfs = {}
for key, value in fdict.items():
    dfs[key] = pd.read_excel(value)
    dfs[key]["Patient"] = key

df = pd.concat(dfs, ignore_index=True)

txt = "P{patid:02d}_F{fibid:02d}"
df["fibid"] = [txt.format(patid=int(patid),fibid=int(fibid)) for patid,fibid in zip(df["Patient"],df["Fibre ID"])]
fibids = sorted(df.fibid.unique())

nrows,ncols = 3,3
speclist = [[{"type": "Scatter3d"} for i in range(0,ncols)] for j in range(0,nrows)]

patids = ["P04","P03","P02","P01"]

zvar = "COX Activity"
if zvar == "COX Activity":
    hovtemp = '<b>mitoID: %{text}</b><br><b>COX: %{marker.color}</b><extra></extra>'
    cmin,cmax = 0.0,255.0
if zvar == "Sphericity":
    hovtemp = '<b>mitoID: %{text}</b><br><b>Sphericity: %{marker.color}</b><extra></extra>'
    cmin,cmax = 0.0,100.0
if zvar == "MCI":
    hovtemp = '<b>mitoID: %{text}</b><br><b>MCI: %{marker.color}</b><extra></extra>'
    cmin,cmax = 0.0,5.0
ttext = zvar+" & spatial distribution of individual mitochondria per fibre: "

for patid in patids:
    patfibs = [x for x in fibids if patid in x]
    Nmits = [len(df["Mito ID"][df["fibid"]==fibid]) for fibid in patfibs]

    fig = make_subplots(
        rows=nrows, cols=ncols,
        specs=speclist,
        subplot_titles=[patfib+"<br>N = "+format(Nmit, ",") for patfib,Nmit in zip(patfibs,Nmits)],
        horizontal_spacing = 0.01,
        vertical_spacing = 0.06)

    for i,fibid in enumerate(patfibs):
        row,col = (i//ncols)+1,(i%ncols)+1
        print("Fibre ID: {fibid} Index: {i:02d} Row: {row:02d} Column: {col:02d}".format(fibid=fibid,i=i,row=row,col=col))
        dffib = df[df["fibid"]==fibid]
        fig.add_trace(
            go.Scatter3d(x=dffib["X"], y=dffib["Y"], z=dffib["Z"],mode='markers',hovertemplate=hovtemp,text = dffib["Mito ID"],
                         marker=dict(size=2,color=[round(x,2) for x in dffib[zvar]],colorscale='Viridis',showscale=True,cmin=cmin,cmax=cmax),showlegend=False),
            row = row,col=col)

    fig.update_layout(height=1440*0.85, width=2560*0.85, title_text=ttext+patid,title_font_size=30)
    fname = os.path.join("..","output",patid+"_"+zvar.replace(" ","_")+".html")
    fig.write_html(fname)
    webbrowser.open_new_tab(fname)

df = df[df["MCI"]<1000]
fig = px.histogram(df, x=zvar, marginal="violin")
fig.write_image(os.path.join("..","output",zvar.replace(" ","_")+"_all.png"),width=2550/2,height=1440/2)
fig = px.histogram(df, x=zvar, color="Patient",marginal="violin")
fig.write_image(os.path.join("..","output",zvar.replace(" ","_")+"_bypatient.png"),width=2550/2,height=1440/2)
