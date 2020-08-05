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
    ''' Returns the ax for a time series scatter plot showing historical
    temperatures. Includes the line of best fit showing the historical trend.

    historical_today: dataframe with the day's historical data
    kind: either 'minimum' or 'maximum' for max or min temperature
    today: the date we are compaing with
    '''

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
    ''' Returns an ax for violin plots showing the historical temperature
    distrubution. One plot for all time and two overlapping plots for Pre 1980
    and post 1980.

    historical_today: dataframe with the day's historical data
    kind: either 'minimum' or 'maximum' for max or min temperature
    today: the date we are compaing with

    '''
    if kind=='maximum':
        col = 'Maximum temperature (°C)'
    elif kind=='minimum':
        col = 'Minimum temperature (°C)'
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

def plot_distribution_alt_text(historical_today, kind, today_date):
    ''' Creates alt text for the distribution graphs
    Alt text "Three violin plots showing the {kind} temperature distribution
    for all time, pre 1980 and post 1980. The all time minimum is {all_time_min}, the maximum is {all_time_max} and
    mean is {all_time_mean}. The pre 1980 minimum is is {pre_min}, the maximum is {pre_max} and
    mean is {pre_mean}. The post 1980 minimum is is {post_min}, the maximum is {post_max} and
    mean is {post_mean}" '''


    if kind=='maximum':
        col = 'Maximum temperature (°C)'
    elif kind=='minimum':
        col = 'Minimum temperature (°C)'
    else:
        return

    all_time_min = historical_today[col].min()
    all_time_max = historical_today[col].max()
    all_time_mean = historical_today[col].mean()

    pre1980 = historical_today[historical_today['Year']<1980]
    pre_min = pre1980[col].min()
    pre_max = pre1980[col].max()
    pre_mean = pre1980[col].mean()

    post1980 = historical_today[historical_today['Year']>=1980]
    post_min = post1980[col].min()
    post_max = post1980[col].max()
    post_mean = post1980[col].mean()


    text = f'Three violin plots showing the {kind} temperature distribution'\
           f'for all time, pre 1980 and post 1980. The all time minimum is '\
           f'{all_time_min}, the maximum is {all_time_max} and the mean is '\
           f'{all_time_mean}. The pre 1980 minimum is is {pre_min}, the '\
           f'maximum is {pre_max} and the mean is {pre_mean}. The post 1980 '\
           f'minimum is is {post_min}, the maximum is {post_max} and the '\
           f'mean is {post_mean}'

    return text




