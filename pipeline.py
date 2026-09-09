from agents import build_extarct_agent,build_search_agent,writer_chian,critics_chain

def run_research_pipeline(topic : str)->dict:
    state={}

    #search agent working 
    print("\n"+"="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent=build_search_agent()

    search_result = search_agent.invoke({
        "messages" : [("user",f"Find recent , reliable and detailed information about the {topic}")]
    })

    state["search_results"] = search_result['messages'][-1].text

    print("\n search resutl ", state['search_results'])


    #step two - reader agent

    print("\n"+"="*50)
    print("step 2 - reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_extarct_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper context.\n\n"
            f"Seach Results:\n{state['search_results'][:800]}"
        )]
    })

    state["scraped_content"]=reader_result['messages'][-1].text


    print("\n scraped content: \n",state['scraped_content'])

    #step 3- writer chain

    print("\n"+"="*50)
    print("step 3 - Writer is drafting your report ...")
    print("="*50)

    research_combined=(
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chian.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n final report \n",state['report'])

    #critic report

    print("\n"+"="*50)
    print("step 4 - Critic is revieving the report ...")
    print("="*50)

    state["feedback"] = critics_chain.invoke({
        "report" : state['report']
    })

    print("\n critic report \n",state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\n Enter a topic : ")
    run_research_pipeline(topic)