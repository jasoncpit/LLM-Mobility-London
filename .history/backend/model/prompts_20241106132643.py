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

You should be highlighting top level agenda of that, for example, Work from home, Work in the office, lunch with friends at a local pub, exercise at the gym. Make the activities mroe diverse and infer from the user_description. 

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
<POI> Home </POI>
<Travel Mode> NONE </Travel Mode>
</07:00>

<07:45>
<Action> Breakfast with partner </Action>
<Location> Stratford, London </Location>
<POI> Home </POI>
<Travel Mode> NONE </Travel Mode>
</07:45>

<08:30>
<Action> Commute by train to West Kensington for work </Action>
<Location> Stratford Station, London </Location>
<POI> Train Station </POI>
<Travel Mode> TRANSIT </Travel Mode>
</08:30>

<09:15>
<Action> Start work </Action>
<Location> West Kensington Office, London </Location>
<POI> Office </POI>
<Travel Mode> NONE </Travel Mode>
</09:15>

<12:30>
<Action> Lunch with colleagues </Action>
<Location> Nearby Café, West Kensington, London </Location>
<POI> Café </POI>
<Travel Mode> WALK </Travel Mode>
</12:30>

(repeat pattern throughout day with 1-2 unique activities)

Instructions: 
1. <Time> Should be in HH:MM format
2. <Action> Can be a single activity, not a combination of activities.  
3. <Location> Should be in Location, City format. You must specify the specific location of the activity. You should not use generic locations like "London", "UK" or "Neaby by City"
4. <POI> Should be a category of point of interest, not a specific point of interest.  
5. The schedule should be achievable, given the user's description and the high level agenda of the day. 
6. You can specify more than granular activities for example, "Commute by train to work" is acceptable. 
7. You should also provide trip to grocery stores and chained with previous activities based on travel. 
8. <Travel Mode> Should be one of the following: NONE, BICYCLE, DRIVE, WALK, TRANSIT
9. Make sure the plan is a directed graph, and the travel mode is consistent between consecutive activities. 
"""



