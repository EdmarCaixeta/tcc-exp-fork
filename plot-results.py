import os
from typing import Tuple
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches   
from scipy.stats import norm
import numpy as np
from my_utils import make_dir

# gambiara p/ plots que o taka pediu
experiment_model = {1: "AlexNet",
                    2: "AlexNet",
                    3: "AlexNet",
                    4: "ResNet18",
                    5: "ResNet18",
                    6: "ResNet18",}

def make_parse() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("srcdir", type=str)
    parser.add_argument("dstdir", type=str)
    parser.add_argument("--delimiter", type=str, default=',')
    parser.add_argument("--bins", type=int, default=20)
    return parser

def read_csv(filename: str, delimiter) -> Tuple[Tuple, Tuple]:
    real = []
    pred = []

    with open(filename, 'r') as csv:
        for line in csv:
            values = line.split(delimiter)
            real.append(float(values[1]))
            pred.append(float(values[2]))
    
    return tuple(real), tuple(pred)

def calc_intersections(hist1, hist2) -> float:
    s = 0
    for p in zip(hist1, hist2):
        s += min(p)
    
    return s

def plot_and_save_histogram(experiment_name: str,
                            real: Tuple, 
                            pred: Tuple, 
                            bins: int, 
                            weights=None) -> None:
    plt.figure()
    
    range_min = min(np.min(real), np.min(pred))
    range_max = max(np.max(real), np.max(pred))
    full_range = (range_min, range_max)

    n1, bins, _ = plt.hist(real, bins=bins,
                                 range=full_range,
                                 weights=weights, 
                                 facecolor="#34a2eb",
                                 edgecolor="#2c5aa3",
                                 alpha=0.9)
    
    n2, bins, _ = plt.hist(pred, bins=bins, 
                                 range=full_range,
                                 weights=weights,
                                 facecolor="#ffbc47",
                              #    edgecolor="#9e742b", 
                                 alpha=0.6)
    
    real_patch = mpatches.Patch(color='#34a2eb', label='y')
    pred_patch = mpatches.Patch(color='#ffbc47', label='ŷ')
    plt.legend(handles=[real_patch, pred_patch])
    
    intersection = calc_intersections(n1, n2)
    plot_nane = f"{experiment_name}-hist-{intersection}.pdf"
    plt.savefig(plot_nane, bbox_inches="tight")

def plot_and_save_data_histogram(data, num_of_bins):
    plt.figure()
    w = np.ones(len(data)) / len(data)
    n, bins, _ = plt.hist(data, 
                           bins=num_of_bins,
                           weights=w,
                           facecolor="#34a2eb",
                           edgecolor="#2c5aa3",
                           alpha=0.9)

    mean = np.mean(data)
    variance = np.var(data)
    half_bin_size = (bins[1] - bins[0]) / 2
    y = norm.pdf(bins, mean, np.sqrt(variance)) * half_bin_size * 2
    plt.plot(bins, y, "--")
    plt.show()
    
def scatter_plot_and_save(experiment_name: str,
                          real: Tuple,
                          pred: Tuple) -> None:
    
    plt.figure()
    plt.xlabel("REAL")
    plt.ylabel("PREDICTION")

    plt.plot(real, pred, 'co')
    
    dashes = [5, 5, 5, 5]
    plt.plot(real, real, dashes=dashes, color="#cccccc")

    plot_name = f"{experiment_name}-scatter.pdf"
    plt.savefig(plot_name, bbox_inches="tight")

def get_metrics(real: Tuple, pred: Tuple) -> Tuple:
    unders = []
    overs = []
    for p in zip(pred, real):
        error = p[0] - p[1]
        if error > 0:
            overs.append(error)
        else:
            unders.append(error)
    
    n = len(real)

    over = np.sum(overs)
    under = np.sum(unders)
    mean_error = (over + under) / n
    mean_abs_error = (over - under) / n
    mse = np.sum([e**2 for e in overs+unders])

    metrics = {"over": over, "under": under, "mean_error": mean_error,
               "MAE": mean_abs_error, "MSE": mse}
    
    return metrics


def plot_rroc_space(metrics: dict, dstdir):
    x = []
    y = []
    names = []
    for e, m in metrics.items():
        x.append(m["over"]/330)
        y.append(m["under"]/330)
        names.append(f"#{e[-1]}")
    
    l = max(np.max(x), abs(np.min(y)))

    plt.figure()
    plt.title("ESPAÇO RROC")
    # under + over = 0
    dashes = [5, 5, 5, 5]
    p = np.linspace(0, 1.8*l, 100)
    plt.plot(p, -p, dashes=dashes, color="#cccccc")

    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    plt.xlim((0, 1.1*l))
    plt.ylim((-1.1*l, 0))
    plt.xlabel("SUPERIOR")
    plt.ylabel("INFERIOR")
    
    for i, p in enumerate(zip(x,y)):
        plt.plot(p[0], p[1], colors[i]+'x')
    
    for i, name in enumerate(names):
        plt.text(x[i]+4, y[i]+4, name, color=colors[i], fontsize=9)

    plt.savefig(f"{dstdir}rroc.pdf")

def plot_rroc_space_zoom(metrics: dict, dstdir):
    x = []
    y = []
    names = []
    for e, m in metrics.items():
        x.append(m["over"] / 330) 
        y.append(m["under"] / 330) 
        names.append(f"#{e[-1]}")
    
    l = max(np.max(x), abs(np.min(y)))

    fig, ax = plt.subplots()
    # plt.figure()
    plt.title("RROC SPACE")

    x_size_caio = 5195.2887
    
    # under + over = 0
    dashes = [5, 5, 5, 5]
    p = np.linspace(0, 1.8*x_size_caio, 100)
    plt.plot(p, -p, dashes=dashes, color="#cccccc")

    # colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    colors = {"AlexNet": 'c', "ResNet18": 'r'}
    
    plt.xlim((0, x_size_caio))
    plt.ylim((-x_size_caio, 0))
    plt.xlabel("OVER")
    plt.ylabel("UNDER")

    def get_model(i: int) -> str:
        if experiment_model[i] == "AlexNet":
            return "AlexNet"
        else:
            return "ResNet18"
    
    for i, p in enumerate(zip(x,y)):
        index = int(names[i].strip('#'))
        model = get_model(index)
        plt.plot(p[0], p[1], colors[model]+'x', 
        label=names[i] + " " + experiment_model[index],markersize=12.0, markeredgewidth=2.0)
    
    for i, name in enumerate(names):
        model = get_model(int(name.strip("#")))
        plt.text(x[i]+4, y[i]+4, name, color=colors[model], fontsize=9)

    plt.legend(loc='upper right', shadow=False)

    #zoom
    axins = ax.inset_axes([0.14, 0.14, 0.35, 0.35])
    x1, x2, y1, y2 = 300, 600, -600, -300
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    # under + over = 0
    dashes = [5, 5, 5, 5]
    p = np.linspace(300, 600, 100)
    axins.plot(p, -p, dashes=dashes, color="#cccccc")

    for i, p in enumerate(zip(x,y)):
        index = int(names[i].strip('#'))
        model = get_model(index)
        axins.plot(p[0], p[1], colors[model]+'x', 
        label=names[i] + " " + experiment_model[index], markersize=12.0, markeredgewidth=2.0)
    
    for i, name in enumerate(names):
        model = get_model(int(name.strip("#")))
        axins.text(x[i]+4, y[i]+4, name, color=colors[model], fontsize=9)
    
    

    # axins.set_xticklabels('')
    # axins.set_yticklabels('')
    ax.indicate_inset_zoom(axins)
    
    plt.savefig(f"{dstdir}rroc.pdf")

if __name__ == "__main__":
    parser = make_parse()
    args = parser.parse_args()

    make_dir(args.dstdir)

    metrics = dict()
    w = None
    for root, _, files in os.walk(args.srcdir):

        for f in sorted(files):
            real, pred = read_csv(root+f, args.delimiter)

            if w is None:
                w = np.ones(len(real)) / len(real)

            experiment_name = f.split('.')[0].replace('#', '')
            experiment_file = args.dstdir + experiment_name
            
            metrics[experiment_name] = get_metrics(real, pred)

            plot_and_save_histogram(experiment_file, 
                                    real, pred, 
                                    args.bins, w)

            scatter_plot_and_save(experiment_file, real, pred)
        
        plot_and_save_data_histogram(real, args.bins)
    
    for key, values in metrics.items():
        print(key)
        print(values)
        print("-"*15)
        print()
    
    # plot_rroc_space(metrics, args.dstdir)
    plot_rroc_space_zoom(metrics, args.dstdir)

