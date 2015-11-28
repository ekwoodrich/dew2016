***standardized poll and data model for dewcaucus*
**

# Political Poll Classification
##A. Horse Race
*Kinda started*

A poll listing two or more candidates and their performance when paired against one another collectively. Presented as a randomized list that reads from a set of predetermined names, and only asks for a response following recitation of all possible options. May include head-to-head polls within the dataset, which are parsed and treated distinctly. This is the most common type of poll and generally includes many more candidates that are believed to be likely to win, which often distorts the results.

##B. Head-to-Head
*Doneish*

A poll containing a question with only two candidates directing the respondent to choose between only the given candidates (although generally provided with an "I don't Know" or "Other" option to prevent distorted results favoring one of the two candidates from an undecided voter, or a voter hesistant to give support to either). This type of poll may produce markedly different data than Horse Race style of polling given the constraints, and can be extremely valuable, especially as a means of weighing the practical legitimacy of candidates. However, incumbents tend to perform somewhat better due to a greater degree of name recognition.

##C. Opinion Poll (Candidate)

A poll that asks respondents to state their personal opinion about various aspects of a politician or candidates performance, positions, are any number of issues. Often conducted as part of other polls, they are parsed and treated distinctly.

For incumbent candidates, this is phrased as some variation of "Approval/Disapproval" or "Job Performance", for individuals not in office, is typically phrased as "Favorable/Unfavorable". Favorable/Unfavorable tends to provide more positive numbers due to lack of activity in an official capacity required by incumbent politicians, and the ability to avoid undesirable topics.


##D. Opinion Poll (Topic)

A poll that ask respondents to state the opinion on broad issues such as national security, gun control, etc. Most critically, the questions do not directly reference a candidate (although this can be abused to lead a voter into responding based on the inference that a position is an indirect reference to a politician). i.e deliberately conflating Obamacare/President Obama with the expectation that the voter will not give a purely policy based response.

##E. Generic Ballot

A poll that contains no specific reference to incumbents or candidates, and instead offers questions that only reference generic, purely hypothetical races. e.g. "If the election for your congressional district were held today, and the candidates were not known, would you vote for the Republican, the Democrat, a different party, or are you unsure?" Provides broad data particularly useful for House elections with limited district-by-district polling and between federal elections.

##F. Aggregate Poll
*Maybe halfway*

An estimate of any variety that has been averaged, or otherwise adjusted based on the results of multiple polls. Often very opaque, and prone to political manipulation, but allows for broad assessment of a race.

##G. Party Identification

A poll that simply asks the respondent to self-identify their partisan affiliation. Most importantly this does *not* necessarily correspond the official party registration of the respondent, and is used to assess trends in popularity of a party versus the issues it advocates.

##H. Name Recognition

A poll that simply asks the respondent whether they are familiar with the candidate or potential candidate in question. "Familiarity" is defined differently from pollster to pollster, but generally only requires having any knowledge about the individual, whether or not it is accurate or extensive.

##I. Election

The official results of a government election. Mainly included for historical data or visualizations.

#Non-Political Data

##A. Economic Data

Data from either public sources (generally the BLS or the Federal Reserve), or private sources (non-politically affiliated) that provide either snapshots or long term information about economic historical trends. Valuable for certain predictions or analysis of present or future performance of a candidate.

##B. Demographics

Information describing the composition of the residents of the United States, including data such as income, religion, ethnicity, etc.


# Structured JSON Formatting (working)

##Bonus: FiveThirtyEight exhaustive ranking of pollster performance. 

Also demonstrates that party affiliation does not necessarily impact accuracy. Public Policy Polling, Democratic affiliated pollster has in the last several election cycles provided highly accurate polling, often the most accurate and dependable for significant races or issues). Similarly, self-asserted "non-biased" pollsters such as Gallup may produce highly inaccurate results despite given greater recognition by the media because of their alleged impartiality.

http://fivethirtyeight.com/interactives/pollster-ratings/