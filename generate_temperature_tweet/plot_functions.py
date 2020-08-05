import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n%100<20 else n%10,"th"))

def linear_regression(x):
    '''
    Returns the linear regression
    x: panda series. The index is the independent variable,
       values are the dependent variable
    '''

    X = x.index.values
    Y = x.values

    n = len(x)

    m = (n*sum(X*Y) - sum(X)*sum(Y)) / (n*sum(X^2) - sum(X)^2)
    b = (sum(Y) - m*sum(X)) / n

    return pd.Series(index=X, data=m*X + b)


def plot_time_series(historical_today, kind, today_date):
    if kind=='maximum':
        col = 'Maximum temperature (°C)'
    elif kind=='minimum':
        col = 'Minimum temperature (°C)'
    else:
        return
    date = f'{suf(today_date.day)} of {today_date.strftime("%B")}'

    ax = historical_today.plot(x='Year',
                               y=col,
                               kind='scatter',
                               label='Historical',
                               title=f'Sydney Observatory Hill {col} for the {date}')

    historical_today[historical_today['Year']==today_date.year].plot(x='Year',
                                                                     y=col,
                                                                     kind='scatter',
                                                                     ax=ax,
                                                                     color='red',
                                                                     label='Today')


    trend_line = linear_regression(historical_today.set_index('Year')[col])

    trend_line.plot(ax=ax,label='Trend')
    plt.legend()
    return ax

def add_label(violin, labels, label):
    ''' Adds a label to a violin plot'''
    color = violin["bodies"][0].get_facecolor().flatten()
    labels.append((mpatches.Patch(color=color), label))

def plot_distribution(historical_today, kind, today_date):
    ''' Plots

    '''
    if kind=='maximum':
        col = 'Maximum temperature (°C)'
        historical_today['rank'] = historical_today[col].rank(method='max')
    elif kind=='minimum':
        col = 'Minimum temperature (°C)'
        historical_today['rank'] = historical_today[col].rank(method='max')
    else:
        return

    date = f'{suf(today_date.day)} of {today_date.strftime("%B")}'

    fig, ax = plt.subplots()

    pre1980 = historical_today.loc[historical_today['Year'] < 1980, col]
    post1980 = historical_today.loc[historical_today['Year'] >= 1980, col]

    labels = []
    alltime = ax.violinplot(dataset=historical_today[col].values,
                            showmeans=True,
                            showextrema=True,
                            points=200,
                            vert=False,
                            positions=[2])
    add_label(alltime, labels, 'All')


    pre = ax.violinplot(dataset=pre1980.values,
                        showmeans=True,
                        showextrema=True,
                        points=200,
                        positions=[1],
                        vert=False)
    add_label(pre, labels, 'Pre 1980')

    post = ax.violinplot(dataset=post1980.values,
                         showmeans=True,
                         showextrema=True,
                         points=200,
                         positions=[1],
                         vert=False)

    add_label(post, labels, 'Post 1980')

    ax.set_title(f'Sydney Observatory Hill {col} for the {date}')
    ax.set_xlabel(col)
    ax.set_ylabel(None)
    ax.yaxis.set_ticks([])
    plt.legend(*zip(*labels), loc=6)

    return ax
