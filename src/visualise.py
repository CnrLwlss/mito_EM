import pandas as pd
pd.set_option('display.max_columns', None)
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import webbrowser

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
            go.Scatter3d(x=dffib["X"], y=dffib["Y"], z=dffib["Z"],mode='markers',hovertemplate='<b>mitoID: %{text}</b><br><b>COX: %{marker.color}</b><extra></extra>',text = dffib["Mito ID"],
                         marker=dict(size=2,color=[round(x,2) for x in dffib["COX Activity"]],colorscale='Viridis',showscale=True,cmin=0.0,cmax=255.0),showlegend=False),
            row = row,col=col)

    fig.update_layout(height=1440*0.85, width=2560*0.85, title_text="COX activity & spatial distribution of individual mitochondria per fibre: "+patid,title_font_size=30)
    fname = os.path.join("..","output",patid+".html")
    fig.write_html(fname)
    webbrowser.open_new_tab(fname)

pats = [1,2,3,4]
#fig = ff.create_distplot([df["COX Activity"][df["Patient"]==str(pat)] for pat in pats], ["Patient "+str(pat) for pat in pats], show_hist=True)

fig = px.histogram(df, x="COX Activity", marginal="violin")
fig.write_image(os.path.join("..","output","COX_all.png"),width=2550/2,height=1440/2)
fig = px.histogram(df, x="COX Activity", color="Patient",marginal="violin")
fig.write_image(os.path.join("..","output","COX_bypatient.png"),width=2550/2,height=1440/2)

#fig.update_yaxes(range=[0, 100], row=1, col=1)
#fig.update_traces(marker_size = 2, row=1,col=2)
#p1 = go.Scatter(x=df["COX Activity"], y=df["Sphericity"],marker_color=[int(x) for x in df["Patient"]],mode='markers')#, hover_data=['Patient','Mito ID'])
#fig.add_trace(
#    p1,
#    row=1, col=1
#)
