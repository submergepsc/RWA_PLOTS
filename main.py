import argparse
import csv
import matplotlib.pyplot as plt


def read_csv(file_name):
    """
    读取csv文件
    :param file_name: csv文件名
    :return: 数据和图例
    """
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # 读取第一行作为图例
        legends = next(reader)
        # 读取其余的行作为数据
        data = [row for row in reader]
    return data, legends


def plot_bar(ax, data, x_label, y_label, title, legends=None):
    """
    绘制柱状图
    :param ax: a matplotlib axes object
    :param data: a list of lists, each inner list is a bar
    :param x_label: x-axis label
    :param y_label: y-axis label
    :param title: plot title
    :param legends: labels for each bar
    """
    x = range(len(data))
    ax.bar(x, [float(i) for i in data], tick_label=legends)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)


def plot_line(ax, data, x_label, y_label, title, legends=None):
    """
    绘制折线图
    :param ax: a matplotlib axes object
    :param data: a list of lists, each inner list is a point
    :param x_label: x-axis label
    :param y_label: y-axis label
    :param title: plot title
    :param legends: labels for each line
    """
    x = range(len(data))
    for i, line_data in enumerate(data):
        ax.plot(x, [float(j) for j in line_data], label=legends[i] if legends else None)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if legends:
        ax.legend(legends)


def plot_box(ax, data, x_label, y_label, title, legends=None):
    """
    绘制箱线图
    :param ax: a matplotlib axes object
    :param data: a list of lists, each inner list is a dataset for a box
    :param x_label: x-axis label
    :param y_label: y-axis label
    :param title: plot title
    :param legends: labels for each box
    """
    ax.boxplot(data)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if legends:
        ax.set_xticklabels(legends)


def main():
    parser = argparse.ArgumentParser(description='Plot experimental results.')
    parser.add_argument('--file', type=str, default='data.csv', help='input csv file')
    parser.add_argument('--output', type=str, default='output.png', help='output file')
    parser.add_argument('--x_label', type=str, default='X', help='x-axis label')
    parser.add_argument('--y_label', type=str, default='Y', help='y-axis label')
    parser.add_argument('--title', type=str, default='Experiment', help='plot title')
    parser.add_argument('--type', type=str, default='bar', help='plot type')
    args = parser.parse_args()

    data, legends = read_csv(args.file)

    fig, ax = plt.subplots()

    if args.type == 'bar':
        plot_bar(ax, data, args.x_label, args.y_label, args.title, legends=legends)
    elif args.type == 'line':
        plot_line(ax, data, args.x_label, args.y_label, args.title, legends=legends)
    elif args.type == 'box':
        # For box plot, data from csv is usually column-wise.
        # Let's transpose it.
        data_transposed = list(map(list, zip(*data)))
        plot_box(ax, data_transposed, args.x_label, args.y_label, args.title, legends=legends)

    fig.savefig(args.output)


if __name__ == '__main__':
    main()