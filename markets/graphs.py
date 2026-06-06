import yfinance as yf # type: ignore
import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import matplotlib.dates as mdates # type: ignore
import matplotlib.ticker as mticker # type: ignore
from datetime import datetime
import os, requests # type: ignore

FRED_API_KEY = os.getenv('FRED_API_KEY', 'FRED_API_KEY_PLACHOLDER')

class yfdata:
    def __init__(self, ticker, start, end, interval):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.interval = interval
        self._table = self.fetch()

    def fetch(self):
        data_table = yf.download(
                self.ticker,
                start = self.start,
                end = self.end,
                interval = self.interval,
                progress = False,
                rounding = True, 
                auto_adjust = True,
                ignore_tz = True,
                )

        data_table.columns = ['Close', 'High', 'Low', 'Open', 'Volume']

        return data_table

    @property
    def table(self):
        return self._table

    def plot(self, count = None, labels = 'y'):
        currency = yf.Ticker(self.ticker).fast_info['currency']
        df = self._table

        # --- Style ---
        BG       = "#ffffff"
        FG       = "#1a2e4a"
        LINE     = "#1a6fb5"
        ANNOT    = "#4a6a8a"
        GRID     = "#dce8f5"

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        ax.plot(df.index, df["Close"], color=LINE, linewidth=1.4, zorder=3) # main line
        ax.fill_between(df.index, df["Close"], alpha=0.12, color=LINE, zorder=2) # opaque fill between line and axis
        low, high = df["Close"].min(), df["Close"].max()
        padding = (high - low) * 0.05

        ax.set_ylim(min(0, low - padding), high * 1.1)

        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

        if labels == 'y':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        elif labels == 'm':
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

        ax.grid(axis="y", color=GRID, linewidth=1, zorder=1)
        ax.grid(axis="x", color=GRID, linewidth=0.5, linestyle=":", zorder=1)

        ax.tick_params(colors=ANNOT, labelsize=12)

        for spine in ax.spines.values():
            spine.set_visible(False)

        start_date_str = datetime.strptime(self.start, '%Y-%m-%d').strftime('%b %Y')
        end_date_str = datetime.strptime(self.end, '%Y-%m-%d').strftime('%b %Y')

        ax.set_title(
            f"{self.ticker} Spot Price ({start_date_str} - {end_date_str})",
            color=FG, fontsize=14, fontweight="bold", pad=14, loc="left"
        )
        ax.set_ylabel(f"Spot Price ({currency})", color=ANNOT, fontsize=10, labelpad=8)
        ax.set_xlabel("", color=ANNOT, fontsize=10, labelpad=8)
        ax.set_xlim(df.index[0], df.index[-1])

        plt.tight_layout()
        plt.savefig(f"{self.ticker}_plot{count}.png", dpi=200, bbox_inches="tight", facecolor=BG)
        print(f"{self.ticker} plot successfully saved.")

class freddata:
    def __init__(self, code, start, end):
        self.code = code
        self.start = start
        self.end = end
        self._table = self.fetch()

    def fetch(self):
        fred_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={self.code}&api_key={FRED_API_KEY}&file_type=json&observation_start={self.start}&observation_end={self.end}'
        json_data = requests.get(fred_url).json()['observations']

        data_table = pd.Series(
                data={pd.Timestamp(d["date"]): float(d["value"]) for d in json_data},
                name = 'value',
                )

        return data_table

    @property
    def table(self):
        return self._table

    def plot(self, count = None, labels = 'y', ylabel = None):
        df = self._table

        # --- Style ---
        BG       = "#ffffff"
        FG       = "#1a2e4a"
        LINE     = "#1a6fb5"
        ANNOT    = "#4a6a8a"
        GRID     = "#dce8f5"

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)

        ax.plot(df.index, df.values, color=LINE, linewidth=1.4, zorder=3) # main line
        ax.fill_between(df.index, df.values, alpha=0.12, color=LINE, zorder=2) # opaque fill between line and axis
        low, high = df.values.min(), df.values.max()
        padding = (high - low) * 0.05

        ax.set_ylim(min(0, low - padding), high * 1.1)

        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))

        if labels == 'y':
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        elif labels == 'm':
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

        ax.grid(axis="y", color=GRID, linewidth=1, zorder=1)
        ax.grid(axis="x", color=GRID, linewidth=0.5, linestyle=":", zorder=1)

        ax.tick_params(colors=ANNOT, labelsize=12)

        for spine in ax.spines.values():
            spine.set_visible(False)

        start_date_str = datetime.strptime(self.start, '%Y-%m-%d').strftime('%b %Y')
        end_date_str = datetime.strptime(self.end, '%Y-%m-%d').strftime('%b %Y')

        ax.set_title(
            f"{self.code} Plot ({start_date_str} - {end_date_str})",
            color=FG, fontsize=14, fontweight="bold", pad=14, loc="left"
        )
        ax.set_ylabel(f"{ylabel}", color=ANNOT, fontsize=10, labelpad=8)
        ax.set_xlabel("", color=ANNOT, fontsize=10, labelpad=8)
        ax.set_xlim(df.index[0], df.index[-1])

        plt.tight_layout()
        plt.savefig(f"{self.code}_plot{count}.png", dpi=200, bbox_inches="tight", facecolor=BG)
        print(f"{self.code} plot successfully saved.")

