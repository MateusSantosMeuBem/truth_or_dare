from random import randint
import discord
from discord.ext import commands
from time import sleep
import pandas as pd

# VICTIM = person who needs to answer
# ASKER = persin who needs to ask

# Matan's solutions for the problem with not seeing
# the members in the room
intents = discord.Intents().all()

client = commands.Bot(command_prefix = '??', case_insensitive = True, intents = intents)
# Pointer that point to the player of the time in memids
turn = 0
# This variable controlls in which turn the game is
global ctrl
ctrl = 0
# Challenges and questions sugestions
global qtn_df
qtn_df = pd.read_excel('questoes.xlsx')
# How many challenges or questions sugestions
global h_qtn_df
h_qtn_df = len(list(qtn_df.index))

# TEST
global memids, mem_vc_id
# Stores the members ids in the voice channel
memids = []
mem_vc_id = []

global vc_channel_id, txt_channel_id, last_ctx, bot_master
# It get the channel with id informed
vc_channel_id = 
txt_channel_id = 
auth_channel_id = 
auth_msg_id =  
last_ctx = None
bot_master = 
# async def counter(time, message):
#   reactions_count = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
#   if time < 0:
#     time = 0
#   elif time > 10:
#     time = 10
  
#   for i in range(len(reactions_count)-1, -1, -1):
#     message.add_reaction(reactions_count[i])
#     sleep(time)
#     message.clear_reaction(reactions_count[i])

# Shows when bot is ready to be used (hehe)
@client.event
async def on_ready():
  print(f'Tamo dentro.\nP.s.: {client.user}')

@client.event
async def on_message(message):
  global memids, txt_channel_id, bot_master
  user = message.author.id
  user_name = client.get_user(user)
  if message.channel.id == txt_channel_id:
    if user not in memids and not message.author.bot:
      await message.delete()
      await user_name.send(f'<@{user}>, você só pode mandar mensagem nesse chat se estiver jogando.')
    await client.process_commands(message)
  elif user == bot_master:
      await client.process_commands(message)
          

@client.event
async def on_raw_reaction_add(payload):
  global memids, mem_vc_id, auth_msg_id, auth_channel_id, vc_channel_id
  voice_channel = client.get_channel(vc_channel_id)
  # Get members in the voice channel
  members = voice_channel.members

  for member in members:
      if member.id not in mem_vc_id:
        mem_vc_id.append(member.id)

  user = client.get_user(payload.user_id)
  # If it is auth message
  if payload.message_id == auth_msg_id:
    # If user is in the voice channel
    if payload.user_id in mem_vc_id:
      if payload.user_id not in memids:
        memids.append(payload.user_id)
        await user.send(f'<@{payload.user_id}>, agora você está no jogo.')
    # If not, remove its reaction
    else:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.remove_reaction("👍", user)
        await user.send(f'<@{payload.user_id}>, você precisa estar no canal de voz para participar.')

@client.event
async def on_raw_reaction_remove(payload):
  global memids, mem_vc_id, auth_msg_id
  user = client.get_user(payload.user_id)
  # If it is auth message
  if payload.message_id == auth_msg_id:
    # If user is in the voice channel
    if payload.user_id in mem_vc_id:
      if payload.user_id in memids:
        memids.remove(payload.user_id)
        await user.send(f'<@{payload.user_id}>, você não pode sair do jogo. Vai pagar por isso!😈')


@client.event
async def on_voice_state_update(ctx, before, after):
    global memids, mem_vc_id, victim, ctrl, turn, txt_channel_id, vc_channel_id, auth_msg_id, last_ctx, asker, victim
    user = ctx.id
    voice_channel = client.get_channel(vc_channel_id)
    txt_channel = client.get_channel(txt_channel_id)
    # Get inside
    b = str(before.channel)
    a = str(after.channel)
    if ((b == 'None' and a != 'None') or (b != 'None' and a != 'None')) and (a != b) and after.channel.id == vc_channel_id:
        if user not in mem_vc_id:
          mem_vc_id.append(user)
        
    # Get out
    elif before.channel is not None and after.channel is None:
      # Remove reaction from auth message
      if user in mem_vc_id:
        mem_vc_id.remove(user)
        channel = client.get_channel(auth_channel_id)
        message = await channel.fetch_message(auth_msg_id)
        user_g = client.get_user(user)
        await message.remove_reaction("👍", user_g)
      # If this user is in the players list, it takes
      # it off
      if user in memids:
        memids.remove(user)
        await ctx.send(f'<@{user}>, você não pode sair do jogo. Vai pagar por isso!😈')
        # If person who left is the victim, it
        # restart round
        try:
          if user == victim:
            await txt_channel.send(f'Nossa vítima <@{user}> saiu da sala. Vamos reiniciar a rodada.')
            ctrl = 0
            turn -= 1
            victim = None
            await iniciar(last_ctx)
              
          elif user == asker:
            await txt_channel.send(f'Aquele que pergunta saiu da sala. Vamos reiniciar a rodada.')
            ctrl = 0
            asker = None
            await iniciar(last_ctx)
        except:
          pass
                
# Starts the turn
@client.command()
async def show_list(ctx):
  global bot_master, memids
  caller = ctx.author.id
  if caller == bot_master:
    # Shows which people are in the game
    string = 'Pessoas participando da brincadeira:\n'
    for id in memids:
      string += f' - <@{id}>\n'
    await ctx.send(f'{string}')

# Starts the turn
@client.command()
async def iniciar(ctx):
  global ctrl, memids, vc_channel_id, last_ctx
  last_ctx = ctx
  caller = ctx.author.id
  if caller in memids:
    if ctrl == 0:
      if len(memids) > 1:
        # Id in balletests = 859232339519602729
        # Id in my server = 774455062491693110
        # It get the channel with id informed
        voice_channel = client.get_channel(vc_channel_id)
        # Get members in the voice channel
        members = voice_channel.members
        # global victim
        # TEST
        # # Stores the members ids in the voice channel
        # memids = [] 

        # for member in members:
        #     if member.id not in memids:
        #       memids.append(member.id)


        global asker
        global turn
        asker = memids[turn]

        # Every new game it goes to the next player
        # if the next player is the last one, it goes
        # to the first one
        if turn < len(memids)-1:
          turn += 1
        else:
          turn = 0

        # Shows which people are in the game
        string = 'Pessoas participando da brincadeira:\n'
        for id in memids:
          string += f' - <@{id}>\n'
        string += f'\n<@{asker}> gire a garrafa.'
        await ctx.send(f'{string}')
        ctrl += 1
      else:
        await ctx.send(f'A partida não pode começar com menos de 2 jogadores.')      
    else:
      await ctx.send(f'<@{caller}>, você não pode iniciar um novo jogo nesse momento.')

@client.command()
async def girar(ctx):
  global ctrl
  caller = ctx.author.id
  if caller in memids:
    if ctrl == 1:
      caller = ctx.author.id
      # The person who called this command hasn't to
      # be the asker
      if caller == asker:
        g = False
        global victim
        # Raffles a person different to the arker to be
        # the victim
        while not g:
          index = randint(0, len(memids) - 1)
          if memids[index] != asker:
            victim = memids[index]
            g = True
        await ctx.send(f'<@{caller}> pergunta para <@{victim}>. Verdade ou consequência?')
        ctrl += 1
      else:
        await ctx.send(f'<@{caller}>, não é sua vez de rodar.')
    else:
        await ctx.send(f'<@{caller}>, você não pode girar a garrafa nesse momento.')

# Command to choose if it's verdade or consequencia
@client.command()
async def op(ctx, op):
  global ctrl
  op = op.lower()
  caller = ctx.author.id
  if caller in memids:
    if ctrl == 2:
      global switch
      caller = ctx.author.id
      if caller == victim:
        if op == 'v':
          await ctx.send(f'<@{asker}>, faça sua pergunta.')
          switch = 'verdade'
          ctrl += 1
        elif op == 'c':
          await ctx.send(f'<@{asker}>, faça seu desafio.')
          switch = 'consequencia'
          ctrl += 1
        else:
          await ctx.send(f'<@{victim}>, você escolheu uma opção incorreta.')
      else:
        await ctx.send(f'<@{caller}>, não é sua vez de escolher.')
    else:
      await ctx.send(f'<@{caller}>, você não pode escolher uma opção agora.')

# Command to be used when asker doesn't know what to ask
@client.command()
async def ajuda(ctx):
  global qtn_df, h_qtn_df, switch, asker
  caller = ctx.author.id
  if caller in memids:
    if ctrl == 3:
      if asker ==  caller:
        df_index = randint(0, h_qtn_df - 1)

        # Looking for a not nan question or challenge
        while str(qtn_df.loc[df_index, switch]).lower() == 'nan':
          df_index = randint(0, h_qtn_df - 1)

        await ctx.send(f'{qtn_df.loc[df_index, switch]}')
      else:
        await ctx.send(f'<@{caller}>, você não pode pedir ajuda agora.')
    else:
      await ctx.send(f'<@{caller}>, você não pode pedir ajuda agora.')

# Command to be used when the challenge or the answer is done
@client.command()
async def feito(ctx):
  global ctrl
  caller = ctx.author.id
  if caller in memids:
    if ctrl == 3:
      if caller == victim:
        # Starts the vote to see if people believe in the victim
        message = await ctx.send("Vocês acreditam nesse cara?")
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        # Wait 10 seconds to finish the vote
        reactions_count = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for i in range(len(reactions_count)-1, -1, -1):
          await message.add_reaction(reactions_count[i])
          sleep(1)
          await message.clear_reaction(reactions_count[i])

        # Gets the reactions (votes)
        updated_message = await ctx.channel.fetch_message(message.id)

        positive = negative = 0
        # Counts the votes
        for r in updated_message.reactions:
            if str(r) == "👍":
                positive = r.count
            elif str(r) == "👎":
                negative = r.count
        # Verifies results
        if positive > negative:
              await ctx.send(f'<@{victim}>, as pessoas acreditaram em você.\nVocê ganhou x coins.')
        elif negative > positive:
              await ctx.send(f'<@{victim}>, as pessoas não acreditaram em você.\nVocê perdeu x coins.')
        else:
              await ctx.send(f'<@{victim}>, as pessoas ficaram na Dúvida.\nVocê falhou.')
        ctrl = 0
        # Starts a new round after 1s
        sleep(1)
        await iniciar(ctx)
      else:
        await ctx.send(f'<@{caller}>, você não pode responder agora.')
    else:
      await ctx.send(f'<@{caller}>, você não pode responder agora.')

# Restarts the game
@client.command()
async def reload(ctx):
  global ctrl, turn, bot_master, asker, victim
  caller = ctx.author.id
  if caller == bot_master:
    ctrl = turn = 0
    victim = asker = None

# Just the game rules
@client.command()
async def regras(ctx):
  rules = 'Olá! Vamos brincar de uma brincadeira bem divertida? 😈\n'
  rules += 'Comandos:\n\n'
  rules += '`??iniciar` - Inicia uma nova partida. Não é possível iniciar enquanto uma outra estiver acontecendo.\n'
  rules += '`??girar` - Sorteia quem irá desafiar quem.\n'
  rules += '`??op` - Escolhe qual das opções a vítima quer. Use `v` ou `c` para escolher.\n'
  rules += '`??ajuda` - Não sabe o que perguntar? Use esse comando que Calux vai te ajudar.\n'
  rules += '`??feito` - A vítima deve usar esse comando quando tiver respondido ou cumprido seu desafio\n\n'
  rules += 'Lembrando que os desafios devem ser provados com uma fotinha ou um vídeo curto. As pessoas decidirão se acreditam ou não.\n\n'
  rules += 'Vamos começar! 😈'
  caller = ctx.author.id
  if caller in memids:
    await ctx.send(f'{rules}')

@client.command()
async def add_message(ctx):
  message = await ctx.send("Você quer participar do jogo? Esteja no canal de voz e reaja ao emoji 👍. \nSe quiser sair, basta retirar a reação ou sair do nala de voz.")
  await message.add_reaction("👍")  

bot_token = ''
client.run(bot_token)
