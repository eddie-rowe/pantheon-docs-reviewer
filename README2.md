# Common Errors

## PR3

openai.RateLimitError: Error code: 429 - {'error': {'message': 'Request too large for gpt-4o in organization org-kcWTmUe32aiccWNeGTidTvW1 on tokens per min (TPM): Limit 30000, Requested 39143. The input or output tokens must be reduced in order to run successfully. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}

openai.RateLimitError: Error code: 429 - {'error': {'message': 'Request too large for gpt-4o in organization org-kcWTmUe32aiccWNeGTidTvW1 on tokens per min (TPM): Limit 30000, Requested 76503. The input or output tokens must be reduced in order to run successfully. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}


## Latest - PR4
openai.RateLimitError: Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-4o in organization org-kcWTmUe32aiccWNeGTidTvW1 on tokens per min (TPM): Limit 30000, Used 26824, Requested 16876. Please try again in 27.4s. Visit https://platform.openai.com/account/rate-limits to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}

Error processing publish message for Demeter_86309706-b43a-4d16-b875-da233560fd73/86309706-b43a-4d16-b875-da233560fd73

  File "/opt/hostedtoolcache/Python/3.11.12/x64/lib/python3.11/site-packages/autogen_agentchat/teams/_group_chat/_chat_agent_container.py", line 133, in on_unhandled_message
    raise ValueError(f"Unhandled message in agent container: {type(message)}")
ValueError: Unhandled message in agent container: <class 'autogen_agentchat.teams._group_chat._events.GroupChatError'>
Error processing publish message for Aphrodite_86309706-b43a-4d16-b875-da233560fd73/86309706-b43a-4d16-b875-da233560fd73