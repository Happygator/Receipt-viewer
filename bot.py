import discord
from discord import app_commands
import os
import io
from dotenv import load_dotenv
import datetime
from ocr_processor import process_image
from chart_generator import generate_pie_chart
import database

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class ReceiptBot(discord.Client):
    def __init__(self):
        # Intents are still needed for connection, though message content might not be strictly needed for interactions.
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync global commands
        # Note: Global sync can take up to an hour to propagate. 
        # For instant updates during dev, sync to a guild=discord.Object(id=...)
        # But for persistent slash commands, this is fine.
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        database.init_db()  # Initialize DB
        print('Ready to process receipts!')

    async def on_message(self, message):
        if message.author == self.user:
            return
            
        # Development utility to force sync slash commands to the current guild
        if message.content.startswith('!sync'):
            print(f"Syncing commands to guild: {message.guild.id}")
            try:
                self.tree.copy_global_to(guild=message.guild)
                await self.tree.sync(guild=message.guild)
                await message.channel.send(f"Successfully synced commands to this server ({message.guild.name}). You should see /analyze now.")
            except Exception as e:
                await message.channel.send(f"Failed to sync: {e}")
                print(f"Sync error: {e}")

client = ReceiptBot()

@client.tree.command(name="analyze", description="Upload a receipt image for analysis")
@app_commands.describe(receipt="The receipt image to analyze")
async def analyze(interaction: discord.Interaction, receipt: discord.Attachment):
    # Defer response because processing might take time (Gemini API)
    await interaction.response.defer(thinking=True)
    
    # Validation
    if not any(receipt.filename.lower().endswith(ext) for ext in ['jpg', 'jpeg', 'png', 'webp']):
        await interaction.followup.send("Please upload a valid image file (jpg, png, webp).")
        return

    try:
        # 1. Download image
        image_bytes = await receipt.read()
        
        # 2. Process with Gemini
        data = process_image(image_bytes)
        items = data.get('items', [])
        
        if not items:
            await interaction.followup.send("Could not identify items. Please checking key/image.")
            return
        
        # 3. Save to Database
        receipt_id = database.save_receipt(data)
        
        # 4. Summarize
        items = data.get('items', [])
        total = sum(item['price'] for item in items)
        item_count = len(items)
        merchant = data.get('merchant', 'Unknown Merchant')
        currency = data.get('currency', 'USD')
        
        # Currency symbol mapping for summary
        currency_symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'KRW': '₩'}
        symbol = currency_symbols.get(currency.upper(), currency + " ")
        
        # Get date from receipt, fallback to today's date if missing
        date_str = data.get('date')
        if not date_str or date_str == 'Unknown Date': # Handle both None and prompt default if any
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')

        chart_title = f"{merchant} Expense Breakdown - {date_str}"

        summary = (
            f"**Processed Receipt**\n"
            f"Found {item_count} items. Total: **{symbol}{total:.2f}**\n"
#            f"_Saved to database (ID: {receipt_id})_"
        )
        
        # 5. Chart
        chart_buf = generate_pie_chart(items, title=chart_title, currency=currency)
        
        files_to_send = []
        if chart_buf:
            files_to_send.append(discord.File(chart_buf, filename="expense_chart.png"))
            
        await interaction.followup.send(content=summary, files=files_to_send)
        
    except Exception as e:
        await interaction.followup.send(f"Error processing receipt: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in .env file.")
    else:
        # Preload OCR engine
        print("Preloading OCR model...")
        import ocr_processor
        ocr_processor.initialize()
        print("OCR model ready.")
        
        client.run(TOKEN)
