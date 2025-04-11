# import discord
# from discord.ext import commands
# import torch
# import logging
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from collections import defaultdict

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Model configuration
# MODEL_CONFIG = {
#     "primary": {
#         "name": "SkolkovoInstitute/roberta_toxicity_classifier",
#         "type": "binary",
#         "base_threshold": 0.35,
#         "toxic_index": 1
#     },
#     "secondary": {
#         "name": "unitary/unbiased-toxic-roberta",
#         "type": "multi-class",
#         "base_threshold": 0.45,
#         "toxic_labels": ['toxicity', 'severe_toxicity', 'obscene', 
#                         'identity_attack', 'insult', 'threat']
#     }
# }

# # Load models and tokenizers
# models = {}
# tokenizers = {}
# for model_name, config in MODEL_CONFIG.items():
#     try:
#         tokenizers[model_name] = AutoTokenizer.from_pretrained(config["name"])
#         models[model_name] = AutoModelForSequenceClassification.from_pretrained(config["name"])
#         logger.info(f"Successfully loaded {model_name} model")
#     except Exception as e:
#         logger.error(f"Failed to load {model_name} model: {str(e)}")
#         raise RuntimeError(f"Model loading failed: {model_name}")

# # Moderation system storage
# mod_data = defaultdict(lambda: {
#     "warnings": defaultdict(int),
#     "enabled": True,
#     "thresholds": {
#         "primary": MODEL_CONFIG["primary"]["base_threshold"],
#         "secondary": MODEL_CONFIG["secondary"]["base_threshold"]
#     },
#     "weights": {
#         "primary": 0.7,
#         "secondary": 0.3
#     }
# })

# class AdvancedModeration(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.max_message_length = 500  # Truncate longer messages

#     def _truncate_text(self, text):
#         return text[:self.max_message_length].rsplit(' ', 1)[0] + '...' if len(text) > self.max_message_length else text

#     async def create_mod_logs(self, guild):
#         try:
#             return await guild.create_text_channel(
#                 "mod-logs",
#                 overwrites={
#                     guild.default_role: discord.PermissionOverwrite(read_messages=False),
#                     guild.me: discord.PermissionOverwrite(
#                         read_messages=True,
#                         send_messages=True,
#                         manage_channels=True
#                     )
#                 },
#                 reason="Moderation logging channel"
#             )
#         except discord.Forbidden:
#             logger.error(f"Missing permissions to create channel in {guild.name}")
#             return None

#     def _analyze_with_model(self, model_name, text):
#         config = MODEL_CONFIG[model_name]
#         try:
#             inputs = tokenizers[model_name](
#                 text,
#                 return_tensors="pt",
#                 truncation=True,
#                 max_length=512
#             )
            
#             with torch.no_grad():
#                 outputs = models[model_name](**inputs)
            
#             if config["type"] == "binary":
#                 score = torch.sigmoid(outputs.logits).item()
#             else:
#                 scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
#                 toxic_indices = [i for i, label in enumerate(models[model_name].config.id2label.values())
#                                if label in config["toxic_labels"]]
#                 score = max(scores[i].item() for i in toxic_indices) if toxic_indices else 0.0
            
#             return score
#         except Exception as e:
#             logger.error(f"Analysis error with {model_name}: {str(e)}")
#             return 0.0

#     def check_toxicity(self, text, guild_id):
#         guild_config = mod_data[guild_id]
        
#         scores = {
#             "primary": self._analyze_with_model("primary", text),
#             "secondary": self._analyze_with_model("secondary", text)
#         }
        
#         logger.info(f"Toxicity scores: {scores}")
        
#         # Check individual thresholds
#         threshold_breach = any(
#             scores[model] > guild_config["thresholds"][model]
#             for model in scores
#         )
        
#         # Calculate weighted score
#         weighted_score = sum(
#             scores[model] * guild_config["weights"][model]
#             for model in scores
#         )
        
#         return threshold_breach or weighted_score > 0.5, scores

#     async def handle_toxic_message(self, message, scores):
#         try:
#             await message.delete()
#             logger.info(f"Deleted toxic message from {message.author}")
#         except discord.Forbidden:
#             logger.error(f"Missing permissions to delete messages in {message.channel.name}")
#             return
#         except discord.NotFound:
#             logger.warning("Message already deleted")
#             return

#         # Warning system
#         guild_id = message.guild.id
#         user_id = message.author.id
#         mod_data[guild_id]["warnings"][user_id] += 1
#         warnings = mod_data[guild_id]["warnings"][user_id]

#         actions = {
#             1: lambda: message.channel.send(
#                 f"⚠️ {message.author.mention}, first warning (1/3).",
#                 delete_after=10
#             ),
#             2: lambda: message.channel.send(
#                 f"⚠️ {message.author.mention}, second warning (2/3).",
#                 delete_after=10
#             ),
#             3: lambda: message.author.timeout(
#                 discord.utils.utcnow() + datetime.timedelta(minutes=30),
#                 reason="3 warnings"
#             ),
#             4: lambda: message.author.ban(
#                 reason="4+ warnings",
#                 delete_message_days=1
#             )
#         }

#         try:
#             if warnings in actions:
#                 await actions[warnings]()
#         except discord.Forbidden:
#             logger.error(f"Missing permissions to punish {message.author}")
#             await message.channel.send("❌ Missing moderation permissions!", delete_after=10)

#         # Logging
#         log_channel = discord.utils.get(message.guild.channels, name="mod-logs") or \
#                      await self.create_mod_logs(message.guild)
        
#         if log_channel:
#             embed = discord.Embed(
#                 title="🚨 Content Moderated",
#                 description=f"**User:** {message.author.mention}\n**Action Taken:** {actions.get(warnings, 'Warning')}",
#                 color=discord.Color.red()
#             )
#             embed.add_field(name="Message", value=self._truncate_text(message.content), inline=False)
#             embed.add_field(name="Scores", value=f"Primary: {scores['primary']:.2f}\nSecondary: {scores['secondary']:.2f}", inline=False)
#             await log_channel.send(embed=embed)

#     @commands.Cog.listener()
#     async def on_message(self, message):
#         if message.author.bot or not message.guild:
#             return

#         guild_id = message.guild.id
#         if not mod_data[guild_id]["enabled"]:
#             return

#         is_toxic, scores = self.check_toxicity(message.content, guild_id)
#         if is_toxic:
#             await self.handle_toxic_message(message, scores)

#     @commands.group(name="modsettings")
#     @commands.has_permissions(administrator=True)
#     async def mod_settings(self, ctx):
#         if ctx.invoked_subcommand is None:
#             embed = discord.Embed(title="⚙️ Moderation Settings", color=0x7289DA)
#             settings = mod_data[ctx.guild.id]
#             embed.add_field(name="Status", value="✅ Enabled" if settings["enabled"] else "❌ Disabled", inline=False)
#             embed.add_field(
#                 name="Thresholds",
#                 value=f"Primary: {settings['thresholds']['primary']:.2f}\nSecondary: {settings['thresholds']['secondary']:.2f}",
#                 inline=False
#             )
#             embed.add_field(
#                 name="Weights",
#                 value=f"Primary: {settings['weights']['primary']:.2f}\nSecondary: {settings['weights']['secondary']:.2f}",
#                 inline=False
#             )
#             await ctx.send(embed=embed, delete_after=30)

#     @mod_settings.command(name="toggle")
#     async def toggle_moderation(self, ctx):
#         mod_data[ctx.guild.id]["enabled"] = not mod_data[ctx.guild.id]["enabled"]
#         status = "enabled" if mod_data[ctx.guild.id]["enabled"] else "disabled"
#         await ctx.send(f"🛡️ Moderation system {status}", delete_after=10)

#     @mod_settings.command(name="set_threshold")
#     async def set_threshold(self, ctx, model_name: str, threshold: float):
#         if model_name not in ["primary", "secondary"]:
#             return await ctx.send("❌ Invalid model name. Use 'primary' or 'secondary'")
        
#         if not 0.1 <= threshold <= 0.9:
#             return await ctx.send("❌ Threshold must be between 0.1 and 0.9")
        
#         mod_data[ctx.guild.id]["thresholds"][model_name] = round(threshold, 2)
#         await ctx.send(f"✅ {model_name} threshold set to {threshold:.2f}", delete_after=10)

#     @mod_settings.command(name="set_weight")
#     async def set_weight(self, ctx, model_name: str, weight: float):
#         if model_name not in ["primary", "secondary"]:
#             return await ctx.send("❌ Invalid model name. Use 'primary' or 'secondary'")
        
#         if not 0.0 <= weight <= 1.0:
#             return await ctx.send("❌ Weight must be between 0.0 and 1.0")
        
#         mod_data[ctx.guild.id]["weights"][model_name] = round(weight, 2)
#         # Automatically adjust other weight
#         other_model = "secondary" if model_name == "primary" else "primary"
#         mod_data[ctx.guild.id]["weights"][other_model] = round(1.0 - weight, 2)
        
#         await ctx.send(
#             f"✅ Weights updated:\n"
#             f"{model_name}: {weight:.2f}\n"
#             f"{other_model}: {1.0 - weight:.2f}",
#             delete_after=15
#         )

#     @commands.command(name="checktox")
#     async def check_toxicity(self, ctx, *, text):
#         is_toxic, scores = self.check_toxicity(text, ctx.guild.id)
#         result = "🚨 TOXIC CONTENT" if is_toxic else "✅ CLEAN"
#         embed = discord.Embed(title="🔍 Toxicity Analysis", color=0xFF5555 if is_toxic else 0x55FF55)
#         embed.add_field(name="Result", value=result, inline=False)
#         embed.add_field(name="Primary Score", value=f"{scores['primary']:.4f}", inline=True)
#         embed.add_field(name="Secondary Score", value=f"{scores['secondary']:.4f}", inline=True)
#         embed.set_footer(text="Thresholds: Primary - {:.2f}, Secondary - {:.2f}".format(
#             mod_data[ctx.guild.id]["thresholds"]["primary"],
#             mod_data[ctx.guild.id]["thresholds"]["secondary"]
#         ))
#         await ctx.send(embed=embed, delete_after=20)

# async def setup(bot):
#     await bot.add_cog(AdvancedModeration(bot))

##### 2 MODELS

# import discord
# from discord.ext import commands
# import torch
# import logging
# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# from collections import defaultdict

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# # Model configuration
# MODEL_CONFIG = {
#     "primary": {
#         "name": "SkolkovoInstitute/roberta_toxicity_classifier",
#         "type": "binary",
#         "base_threshold": 0.35,
#         "toxic_index": 1
#     },
#     "secondary": {
#         "name": "unitary/unbiased-toxic-roberta",
#         "type": "multi-class",
#         "base_threshold": 0.45,
#         "toxic_labels": ['toxicity', 'severe_toxicity', 'obscene',
#                          'identity_attack', 'insult', 'threat']
#     }
# }

# # Load models and tokenizers
# models = {}
# tokenizers = {}
# for model_name, config in MODEL_CONFIG.items():
#     try:
#         tokenizers[model_name] = AutoTokenizer.from_pretrained(config["name"])
#         models[model_name] = AutoModelForSequenceClassification.from_pretrained(config["name"])
#         logger.info(f"Successfully loaded {model_name} model")
#     except Exception as e:
#         logger.error(f"Failed to load {model_name} model: {str(e)}")
#         raise RuntimeError(f"Model loading failed: {model_name}")

# # Moderation system storage
# mod_data = defaultdict(lambda: {
#     "warnings": defaultdict(int),
#     "enabled": True,
#     "thresholds": {
#         "primary": MODEL_CONFIG["primary"]["base_threshold"],
#         "secondary": MODEL_CONFIG["secondary"]["base_threshold"]
#     },
#     "weights": {
#         "primary": 0.7,
#         "secondary": 0.3
#     }
# })

# class AdvancedModeration(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.max_message_length = 500  # Truncate longer messages

#     def _truncate_text(self, text):
#         return text[:self.max_message_length].rsplit(' ', 1)[0] + '...' if len(text) > self.max_message_length else text

#     async def create_mod_logs(self, guild):
#         try:
#             return await guild.create_text_channel(
#                 "mod-logs",
#                 overwrites={
#                     guild.default_role: discord.PermissionOverwrite(read_messages=False),
#                     guild.me: discord.PermissionOverwrite(
#                         read_messages=True,
#                         send_messages=True,
#                         manage_channels=True
#                     )
#                 },
#                 reason="Moderation logging channel"
#             )
#         except discord.Forbidden:
#             logger.error(f"Missing permissions to create channel in {guild.name}")
#             return None

#     def _analyze_with_model(self, model_name, text):
#         config = MODEL_CONFIG[model_name]
#         try:
#             inputs = tokenizers[model_name](
#                 text,
#                 return_tensors="pt",
#                 truncation=True,
#                 max_length=512
#             )
#             with torch.no_grad():
#                 outputs = models[model_name](**inputs)
            
#             if config["type"] == "binary":
#                 score = torch.sigmoid(outputs.logits)[0][config["toxic_index"]].item()
#             else:
#                 scores = torch.nn.functional.softmax(outputs.logits, dim=1)[0]
#                 toxic_indices = [i for i, label in enumerate(models[model_name].config.id2label.values())
#                                  if label in config["toxic_labels"]]
#                 score = max(scores[i].item() for i in toxic_indices) if toxic_indices else 0.0

#             return score
#         except Exception as e:
#             logger.error(f"Analysis error with {model_name}: {str(e)}")
#             return 0.0

#     def check_toxicity(self, text, guild_id):
#         guild_config = mod_data[guild_id]

#         scores = {
#             model_name: self._analyze_with_model(model_name, text)
#             for model_name in MODEL_CONFIG
#         }

#         combined_score = sum(
#             scores[m] * guild_config["weights"][m] for m in scores
#         )

#         toxic = any(
#             scores[m] >= guild_config["thresholds"][m]
#             for m in scores
#         )

#         logger.info(f"Toxicity check for guild {guild_id} | Scores: {scores} | Combined: {combined_score:.2f} | Flagged: {toxic}")
#         return toxic, scores

#     @commands.Cog.listener()
#     async def on_message(self, message):
#         if message.author.bot or not message.guild:
#             return

#         guild_id = message.guild.id
#         if not mod_data[guild_id]["enabled"]:
#             return

#         truncated = self._truncate_text(message.content)
#         is_toxic, scores = self.check_toxicity(truncated, guild_id)

#         if is_toxic:
#             mod_data[guild_id]["warnings"][message.author.id] += 1
#             try:
#                 await message.delete()
#             except discord.Forbidden:
#                 logger.warning(f"Missing permission to delete message in {message.guild.name}")

#             # Get or create mod-logs channel
#             log_channel = discord.utils.get(message.guild.text_channels, name="mod-logs")
#             if not log_channel:
#                 log_channel = await self.create_mod_logs(message.guild)

#             embed = discord.Embed(
#                 title="Toxic Message Deleted",
#                 description=f"**User:** {message.author.mention}\n**Content:** {truncated}",
#                 color=discord.Color.red()
#             )
#             embed.add_field(name="Model Scores", value='\n'.join(f"{k}: `{v:.2f}`" for k, v in scores.items()), inline=False)
#             embed.set_footer(text=f"Warnings: {mod_data[guild_id]['warnings'][message.author.id]}")
#             if log_channel:
#                 await log_channel.send(embed=embed)
#             else:
#                 await message.channel.send(embed=embed)

# # Setup function
# async def setup(bot):
#     await bot.add_cog(AdvancedModeration(bot))

import discord
from discord.ext import commands
import torch
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model setup
MODEL_NAME = "SkolkovoInstitute/roberta_toxicity_classifier"
TOXIC_THRESHOLD = 0.35  # You can adjust this
TOXIC_INDEX = 1

# Load tokenizer and model
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    logger.info("Toxicity model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise RuntimeError("Model loading failed.")

# Per-guild moderation data
mod_data = defaultdict(lambda: {
    "warnings": defaultdict(int),
    "enabled": True,
    "threshold": TOXIC_THRESHOLD
})

class AdvancedModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.max_length = 500  # Limit for long messages

    def _truncate(self, text):
        return text[:self.max_length].rsplit(' ', 1)[0] + '...' if len(text) > self.max_length else text

    def check_toxicity(self, text, guild_id):
        try:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
            score = torch.sigmoid(outputs.logits)[0][TOXIC_INDEX].item()
            logger.info(f"Toxicity score for guild {guild_id}: {score}")
            return score >= mod_data[guild_id]["threshold"]
        except Exception as e:
            logger.error(f"Toxicity check failed: {e}")
            return False

    async def create_mod_logs(self, guild):
        try:
            return await guild.create_text_channel(
                "mod-logs",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                },
                reason="For moderation logs"
            )
        except discord.Forbidden:
            logger.warning(f"Missing permissions to create mod-logs in {guild.name}")
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        guild_id = message.guild.id
        if not mod_data[guild_id]["enabled"]:
            return

        text = self._truncate(message.content)
        if self.check_toxicity(text, guild_id):
            mod_data[guild_id]["warnings"][message.author.id] += 1

            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, your message was flagged as toxic and has been removed.",
                    delete_after=10
                )
            except discord.Forbidden:
                logger.warning(f"Missing permissions to delete message or warn user in {message.guild.name}")

            mod_channel = discord.utils.get(message.guild.text_channels, name="mod-logs")
            if not mod_channel:
                mod_channel = await self.create_mod_logs(message.guild)

            if mod_channel:
                await mod_channel.send(
                    f"🚨 **Toxic Message Removed**\n"
                    f"👤 **User:** {message.author} ({message.author.id})\n"
                    f"📝 **Message:** {text}\n"
                    f"⚠️ **Warnings:** {mod_data[guild_id]['warnings'][message.author.id]}"
                )

# Setup function for cog
async def setup(bot):
    await bot.add_cog(AdvancedModeration(bot))
