import os
import anthropic
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

app = App(token=SLACK_BOT_TOKEN)
claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

KNOWLEDGE_BASE = """
[Reports]
Q: How to fix N/A in Placement report?
A: Double check the Data Update tab. Column B contains the campaign name. Compare it to the USA tab using CTRL+F. Usually a small space or dash makes the difference. Also remove dollar symbols via CTRL+H (Find: dollar sign, Replace: empty).

Q: How to sort Placement reports properly?
A: Click the 2nd row (column headers), click filter. Sort by Placement type Z to A, then Campaign Z to A, then column O Spent Yesterday Z to A.

Q: Can Search Term Harvesting Report not have Total New Search Terms?
A: Yes. Adjust criteria in the Criteria tab. Change Min Orders, Max ACOS, Min Clicks, Min CVR depending on how strict you want the filter.

Q: What is the difference between Bleeders 1.0 and Bleeders 2.0?
A: Bleeders 1.0 is everything with zero orders bleeding money, filter Orders=0 and Clicks above 10. Bleeders 2.0 is everything converted but at unprofitable ACOS, filter Clicks above 10 and ACOS above breakeven e.g. 55%.

[General]
Q: How do I request a day off?
A: Reach out to Megon Stefanovski in HR and also notify your manager.

Q: Who do I tag when I write threads?
A: Tag your team manager.

[Tasks]
Q: How many tasks are enough per day?
A: 15 to 20 basic tasks per day is mandatory. If you do not fulfil this, consider taking on another client.

Q: How long does it take to get a new client?
A: There is no fixed threshold. Notify your manager that you are ready and willing to commit to another client.
"""

SYSTEM_PROMPT = f"""You are KTG Bot, a friendly internal assistant for the KTG team.
Answer using ONLY the knowledge base below. Be concise and clear.
If the answer is not in the knowledge base reply: I don't have that info, please reach out to your manager or team lead.
End every reply with: KTG Bot

Knowledge Base:
{KNOWLEDGE_BASE}
"""

@app.event("message")
def handle_dm(event, say, logger):
    if event.get("channel_type") != "im":
        return
    if event.get("bot_id"):
        return
    user_message = event.get("text", "").strip()
    if not user_message:
        return
    try:
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.content[0].text
    except Exception as e:
        reply = "Sorry, I am having trouble. Please reach out to your manager or team lead. KTG Bot"
    say(reply)

print("KTG Bot is starting...")
SocketModeHandler(app, SLACK_APP_TOKEN).start()
