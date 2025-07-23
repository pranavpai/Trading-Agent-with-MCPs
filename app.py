import gradio as gr
from util import css, js, Color
import pandas as pd
from trading_floor import names, lastnames, short_model_names
import plotly.express as px
from accounts import Account
from database import read_log, read_log_prioritized, read_mcp_tool_logs

mapper = {
    "trace": Color.WHITE,
    "agent": Color.CYAN,
    "function": Color.GREEN,
    "generation": Color.YELLOW,
    "response": Color.MAGENTA,
    "account": Color.RED,
    "mcp_tool": Color.BLUE,
}


class Trader:
    def __init__(self, name: str, lastname: str, model_name: str):
        self.name = name
        self.lastname = lastname
        self.model_name = model_name
        self.account = Account.get(name)

    def reload(self):
        self.account = Account.get(self.name)

    def get_title(self) -> str:
        return f"<div style='text-align: center;font-size:34px;'>{self.name}<span style='color:#ccc;font-size:24px;'> ({self.model_name}) - {self.lastname}</span></div>"

    def get_strategy(self) -> str:
        return self.account.get_strategy()

    def get_portfolio_value_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.account.portfolio_value_time_series, columns=["datetime", "value"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df

    def get_portfolio_value_chart(self):
        df = self.get_portfolio_value_df()
        fig = px.line(df, x="datetime", y="value")
        margin = dict(l=40, r=20, t=20, b=40)
        fig.update_layout(
            height=300,
            margin=margin,
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="#bbb",
            plot_bgcolor="#dde",
        )
        fig.update_xaxes(tickformat="%m/%d", tickangle=45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=8), tickformat=",.0f")
        return fig

    def get_holdings_df(self) -> pd.DataFrame:
        """Convert holdings to DataFrame for display"""
        holdings = self.account.get_holdings()
        if not holdings:
            return pd.DataFrame(columns=["Symbol", "Quantity"])

        df = pd.DataFrame(
            [{"Symbol": symbol, "Quantity": quantity} for symbol, quantity in holdings.items()]
        )
        return df

    def get_transactions_df(self) -> pd.DataFrame:
        """Convert transactions to DataFrame for display"""
        transactions = self.account.list_transactions()
        if not transactions:
            return pd.DataFrame(columns=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"])

        return pd.DataFrame(transactions)

    def get_portfolio_value(self) -> str:
        """Calculate total portfolio value based on current prices"""
        portfolio_value = self.account.calculate_portfolio_value() or 0.0
        pnl = self.account.calculate_profit_loss(portfolio_value) or 0.0
        color = "green" if pnl >= 0 else "red"
        emoji = "⬆" if pnl >= 0 else "⬇"
        return f"<div style='text-align: center;background-color:{color};'><span style='font-size:32px'>${portfolio_value:,.0f}</span><span style='font-size:24px'>&nbsp;&nbsp;&nbsp;{emoji}&nbsp;${pnl:,.0f}</span></div>"

    def get_logs(self, previous=None) -> str:
        logs = read_log_prioritized(self.name, last_n=13)
        response = ""
        for log in logs:
            timestamp, type, message = log
            color = mapper.get(type, Color.WHITE).value
            # Format account logs specially for trading activity
            if type == "account":
                response += f"<span style='color:{color}; font-weight:bold'>{timestamp.split()[1]} : 💰 {message}</span><br/>"
            else:
                response += f"<span style='color:{color}'>{timestamp.split()[1]} : [{type}] {message}</span><br/>"
        response = f"<div style='height:250px; overflow-y:auto; background: #1a1a1a; padding: 8px; border-radius: 4px;'>{response}</div>"
        return response

    def get_mcp_tool_logs(self, previous=None) -> str:
        logs = read_mcp_tool_logs(self.name, last_n=10)
        response = ""
        for log in logs:
            timestamp, type, message = log
            color = mapper.get(type, Color.BLUE).value
            # Clean up the message format - remove redundant timestamp formatting
            clean_message = message.replace("🔧 ", "")
            response += f"<span style='color:{color}; font-weight:bold'>{timestamp.split()[1]} : 🔧 {clean_message}</span><br/>"
        
        if not response:
            response = "<span style='color:#666; font-style:italic'>No MCP tool calls yet...</span><br/>"
            
        response = f"<div style='height:250px; overflow-y:auto; background: #1a1a1a; padding: 8px; border-radius: 4px;'>{response}</div>"
        return response


class TraderView:
    def __init__(self, trader: Trader):
        self.trader = trader
        self.portfolio_value = None
        self.chart = None
        self.holdings_table = None
        self.transactions_table = None
        self.activity_log = None
        self.tool_log = None

    def make_ui(self):
        with gr.Column():
            gr.HTML(self.trader.get_title())
            with gr.Row():
                self.portfolio_value = gr.HTML(value=self.trader.get_portfolio_value())
            with gr.Row():
                self.chart = gr.Plot(
                    value=self.trader.get_portfolio_value_chart(),
                    container=True, 
                    show_label=False
                )
            with gr.Row(variant="panel"):
                with gr.Column(scale=1):
                    gr.HTML("<h4 style='color: #00dddd; margin: 5px 0;'>📊 Trading Activity</h4>")
                    self.activity_log = gr.HTML(value=self.trader.get_logs())
                with gr.Column(scale=1):
                    gr.HTML("<h4 style='color: #0066ff; margin: 5px 0;'>🔧 MCP Tool Calls</h4>")
                    self.tool_log = gr.HTML(value=self.trader.get_mcp_tool_logs())
            with gr.Row():
                self.holdings_table = gr.Dataframe(
                    value=self.trader.get_holdings_df(),
                    label="Holdings",
                    headers=["Symbol", "Quantity"],
                    row_count=(5, "dynamic")
                )
            with gr.Row():
                self.transactions_table = gr.Dataframe(
                    value=self.trader.get_transactions_df(),
                    label="Recent Transactions",
                    headers=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"],
                    row_count=(5, "dynamic")
                )

    def refresh_all(self):
        """Refresh all components - called by timer"""
        self.trader.reload()
        return [
            self.trader.get_portfolio_value(),
            self.trader.get_portfolio_value_chart(),
            self.trader.get_logs(),
            self.trader.get_mcp_tool_logs(),
            self.trader.get_holdings_df(),
            self.trader.get_transactions_df(),
        ]

    def refresh_fast(self):
        """Fast refresh for logs only - called by fast timer"""
        return [
            self.trader.get_logs(),
            self.trader.get_mcp_tool_logs(),
        ]


# Main UI construction
def create_ui():
    """Create the main Gradio UI for the trading simulation with real-time streaming updates"""

    traders = [
        Trader(trader_name, lastname, model_name)
        for trader_name, lastname, model_name in zip(names, lastnames, short_model_names)
    ]
    trader_views = [TraderView(trader) for trader in traders]

    with gr.Blocks(
        title="🔴 LIVE Trading Dashboard", 
        css=css, 
        js=js, 
        theme=gr.themes.Default(primary_hue="sky"), 
        fill_width=True
    ) as ui:
        # Add a status indicator at the top
        gr.HTML("""
            <div style='text-align: center; background: linear-gradient(90deg, #ff6b6b, #4ecdc4); 
                        padding: 10px; margin-bottom: 20px; border-radius: 8px;'>
                <h2 style='color: white; margin: 0;'>🔴 LIVE Trading Dashboard - Real-Time Updates</h2>
                <p style='color: white; margin: 5px 0 0 0; font-size: 14px;'>
                    📊 Logs streaming every 1s | 💰 Portfolio every 3s | 📈 Charts every 5s
                </p>
            </div>
        """)
        
        with gr.Row():
            for trader_view in trader_views:
                trader_view.make_ui()

        # Create timers for different update frequencies
        fast_timer = gr.Timer(1.0)  # 1 second for logs
        medium_timer = gr.Timer(3.0)  # 3 seconds for portfolio/holdings  
        slow_timer = gr.Timer(5.0)  # 5 seconds for charts

        # Set up fast refresh (logs only) for all traders
        for trader_view in trader_views:
            fast_timer.tick(
                fn=trader_view.refresh_fast,
                outputs=[trader_view.activity_log, trader_view.tool_log],
                show_progress="hidden"
            )

        # Set up medium refresh (portfolio and holdings) for all traders  
        for trader_view in trader_views:
            medium_timer.tick(
                fn=lambda tv=trader_view: [tv.trader.get_portfolio_value(), tv.trader.get_holdings_df(), tv.trader.get_transactions_df()],
                outputs=[trader_view.portfolio_value, trader_view.holdings_table, trader_view.transactions_table],
                show_progress="hidden"
            )

        # Set up slow refresh (charts) for all traders
        for trader_view in trader_views:
            slow_timer.tick(
                fn=lambda tv=trader_view: tv.trader.get_portfolio_value_chart(),
                outputs=[trader_view.chart],
                show_progress="hidden"
            )

        # Add refresh status footer
        gr.HTML("""
            <div style='text-align: center; margin-top: 20px; padding: 10px; 
                        background: #2d3748; border-radius: 8px;'>
                <p style='color: #a0aec0; margin: 0; font-size: 12px;'>
                    🚀 Real-time streaming enabled | Last updated: <span id='last-update'></span>
                </p>
            </div>
            <script>
                setInterval(() => {
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                }, 1000);
            </script>
        """)

    return ui


if __name__ == "__main__":
    print("Starting Real-Time Trading Dashboard...")
    ui = create_ui()
    print("✓ UI created successfully with real-time streaming")
    print("📊 Logs stream every 1 second")
    print("💰 Portfolio updates every 3 seconds") 
    print("📈 Charts update every 5 seconds")
    print("🌐 Launching server on http://127.0.0.1:7860")
    ui.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=False,
        share=False,
        show_error=True
    )
