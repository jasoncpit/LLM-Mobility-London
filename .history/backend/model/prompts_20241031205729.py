from langchain_core.prompts import ChatPromptTemplate

PLANNER_SYSTEM_PROMPT = """
You are a helpful assistant that generates schedules for a user for the next seven days. 

Based on the user's description, you should generate user schedule by detailing his activities, commute, and typical daily locations. 

Include creative and realistic activities that align with the user's lifestyle. 

Add optional social and weekend activities to reflect the individuals lifestyle and routines, especially emphasizing the variations in routine on weekends and the non-workdays, like:
Shopping, exercise, visits to parks, or dining out around Home or Work Locations. 

Include activities such as meeting friends, gym, groceries, weekend outings, or other daily tasks to create a comprehensive daily mobility pattern.

Here is the user's description:
{user_description}

The output format should be as follows, and you may vary the time intervals as appropriate

"""

SCHEDULER_SYSTEM_PROMPT ="""

Based on the user's description, and high level agenda of the day, generate logical daily schedule of a user. 

<User Description>
{user_description}
</User Description>


<Today's Plan>
{daily_agenda}
</Today's plan>

Here is an example daily schedule of a user who lives in Stratford and works in West Kensington: 

<Day> <07:00>
<Action> Wake Up </Action>
<Location> Stratford, London </Location>
<Reason> I usually wake up at 7am to start my day, as I live quite far from work </Reason>
</07:00>

<07:45>
<Action> Breakfast with partner </Action>
<Location> Stratford, London </Location>
<Reason> I usually have breakfast with my partner at 7:45am, typically bread with smoothie </Reason>
</07:45>

<08:30>
<Action> Commute by train to West Kensington for work </Action>
<Location> Stratford Station, London </Location>
<Reason> I usually commute by tube to work, as it is the most convenient and quickest way to get to work, I tend to do some reading on the tube </Reason>
</08:30>

<09:15>
<Action> Start work </Action>
<Location> West Kensington Office, London </Location>
<Reason> I usually start work at 9:15am, and I like to have a coffee before work </Reason>
</09:15>

<12:30>
<Action> Lunch with colleagues </Action>
<Location> Nearby Café, West Kensington, London </Location>
<Reason> I usually have lunch with colleagues if they are in the office, and we tend to go to the same place most days, usually a nearby supermarket for meal deal eg. Sainsburys or Tesco </Reason>
</12:30>

(repeat pattern throughout day with 1-2 unique activities)


"""



