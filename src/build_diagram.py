"""Render the actual pipeline topology; no generated decorative imagery."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from src.config import DOC

def build_diagram():
    fig,ax=plt.subplots(figsize=(12,8));ax.set(xlim=(0,12),ylim=(-.3,9));ax.axis('off')
    fig.patch.set_facecolor('#F5F7FA')
    ax.text(.4,8.5,'Workforce & Recruiting Analytics Pipeline',fontsize=19,weight='bold',color='#183153')
    ax.text(.4,8.05,'Synthetic educational data • Python + SQLite + Excel',fontsize=11,color='#45556B')
    nodes={'emp':(2.2,6.8,'Monthly employee files\ndata/raw/employees/'),'rec':(8.5,6.8,'Recruiting cohort files\ndata/raw/recruiting/'),'clean1':(2.2,5.2,'Load, clean and validate\nload_data / clean_data / quality_checks'),'clean2':(8.5,5.2,'Load, clean and validate\nload_data / clean_data / quality_checks'),'transform':(2.2,3.6,'Employee flags and aggregation\ntransform + optimization strategies'),'recruit':(8.5,3.6,'As-of recruiting aggregation\nbuild_kpis.py'),'join':(5.3,2,'One-to-one group join + KPI ratios\nMonth / department / fictional site'),'output':(5.3,.4,'CSV outputs + Excel + executed EDA\nSQL reconciliation and validation logs')}
    for key,(x,y,label) in nodes.items():
        ax.add_patch(FancyBboxPatch((x-2,y-.43),4,.86,boxstyle='round,pad=0.08',facecolor='#FFFFFF',edgecolor='#7190AE',linewidth=1.3))
        ax.text(x,y,label,ha='center',va='center',fontsize=9.8,color='#183153',linespacing=1.6)
    for a,b in [('emp','clean1'),('rec','clean2'),('clean1','transform'),('clean2','recruit'),('transform','join'),('recruit','join'),('join','output')]:
        x,y,_=nodes[a];u,v,_=nodes[b]
        ax.annotate('',xy=(u,v+.5),xytext=(x,y-.5),arrowprops={'arrowstyle':'->','color':'#2B6F93','lw':1.7})
    fig.savefig(DOC/'workflow_diagram.png',dpi=160,bbox_inches='tight');plt.close(fig)
