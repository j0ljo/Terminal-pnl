from rich.console import Console
from rich.table import Table
from rich.theme import Theme
from rich.style import Style
from rich import box
import pandas as pd
import os

# Custom theme for hacker aesthetic
custom_theme = Theme({
    "info": "green",
    "warning": "red",
    "header": "bold cyan",
    "profit": "bold green",
    "loss": "bold red"
})

console = Console(theme=custom_theme)

class TradingJournal:
    def __init__(self, file_path):
        self.file_path = file_path
        self.load_data()

    def load_data(self):
        """Load trading data from CSV/XLSX file"""
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        try:
            if file_extension == '.csv':
                self.data = pd.read_csv(self.file_path, encoding='utf-8')
            elif file_extension in ['.xlsx', '.xls']:
                self.data = pd.read_excel(self.file_path)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            
            # Convert date column to datetime if it exists
            if 'date' in self.data.columns:
                self.data['date'] = pd.to_datetime(self.data['date'])
                
        except FileNotFoundError:
            console.print(f"[warning]Error: File {self.file_path} not found.[/warning]")
            self.data = pd.DataFrame()
        except Exception as e:
            console.print(f"[warning]Error loading file: {str(e)}[/warning]")
            self.data = pd.DataFrame()

    def display_trades(self):
        """Display trades in a styled table"""
        if self.data.empty:
            console.print("[warning]No trading data available.[/warning]")
            return

        # Create table
        table = Table(
            show_header=True,
            header_style="header",
            box=box.HEAVY,
            border_style="cyan",
            title="Trading Journal",
            title_style="bold cyan"
        )

        # Add columns
        columns = ["Date", "Session", "Quantity", "Risk:Reward", "PnL", "% Change", "Comments"]
        for column in columns:
            table.add_column(column, justify="center")

        # Add rows
        for _, row in self.data.iterrows():
            try:
                # Handle PnL conversion more safely
                pnl_str = str(row['PnL']).strip()
                pnl_value = float(pnl_str.replace('$', '').replace(',', ''))
                pnl_style = "profit" if pnl_value >= 0 else "loss"
                
                table.add_row(
                    str(row['date'].strftime('%Y-%m-%d')),
                    str(row['trading session']),
                    str(row['quantity']),
                    str(row['risk:reward']),
                    f"[{pnl_style}]{pnl_str}[/{pnl_style}]",
                    f"{row['percentage change']}%",
                    str(row['comments'])
                )
            except Exception as e:
                console.print(f"[warning]Error processing row: {str(e)}[/warning]")
                continue

        # Clear screen (works on both Windows and Unix-like systems)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Display header
        console.print("\n[bold green]=== TRADING PERFORMANCE ANALYZER ===\n", justify="center")
        
        # Display table
        console.print(table)
        
        # Display summary statistics
        self.display_summary()

    def display_summary(self):
        """Display summary statistics"""
        if not self.data.empty:
            try:
                total_trades = len(self.data)
                pnl_values = self.data['PnL'].str.replace('$', '').str.replace(',', '').astype(float)
                profitable_trades = sum(pnl_values > 0)
                
                console.print("\n[bold cyan]=== Summary Statistics ===", justify="center")
                console.print(f"Total Trades: {total_trades}")
                console.print(f"Profitable Trades: [profit]{profitable_trades}[/profit]")
                console.print(f"Loss Making Trades: [loss]{total_trades - profitable_trades}[/loss]")
                
                if total_trades > 0:
                    win_rate = (profitable_trades/total_trades) * 100
                    console.print(f"Win Rate: [{'profit' if win_rate >= 50 else 'loss'}]{win_rate:.2f}%[/]")
                    console.print(f"Total P&L: [{'profit' if pnl_values.sum() >= 0 else 'loss'}]${pnl_values.sum():.2f}[/]")
            except Exception as e:
                console.print(f"[warning]Error calculating statistics: {str(e)}[/warning]")

def main():
    # Get the current script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the CSV file
    csv_path = os.path.join(script_dir, "trading_journal.csv")
    
    # Create journal instance with full path
    journal = TradingJournal(csv_path)
    journal.display_trades()

if __name__ == "__main__":
    main()
