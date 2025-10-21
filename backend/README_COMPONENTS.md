# Internal Backend Notes

`ai_agent.AIAgent.handle_incoming` does the main flow:

- Consult KB via `KBService.find_answer`
- If found: `NotificationService.notify_customer`
- Else: `HelpRequestService.create_help_request` then `NotificationService.notify_supervisor`

`HelpRequestService.check_and_mark_timeouts` is used by background worker to set unresolved.
