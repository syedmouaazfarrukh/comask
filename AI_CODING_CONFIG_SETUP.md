# AI Coding Config Setup

This repository has been configured to use [TechNickAI's ai-coding-config](https://github.com/TechNickAI/ai-coding-config) for standardized AI-assisted development.

## What's Been Set Up

✅ Cloned ai-coding-config to `~/.ai_coding_config`  
✅ Created `.cursor/commands/` and `.cursor/rules/` directories  
✅ Created `.claude/commands/` directory  
✅ Copied the `/ai-coding-config` command

## Next Steps

### For Cursor Users

1. **Run the setup command in Cursor:**
   ```
   /ai-coding-config
   ```
   
   This interactive command will:
   - Detect your tech stack (Python, React, etc.)
   - Let you choose relevant coding rules
   - Set up commands and agents
   - Configure a personality (optional)

2. **Load project-specific rules:**
   ```
   /load-rules
   ```
   
   This automatically loads relevant coding standards based on what you're working on.

### Available Commands (after setup)

- `/load-rules` - Load coding standards for current task
- `/address-pr-comments` - Handle PR feedback automatically
- `/autotask "description"` - Autonomous feature development
- `/troubleshoot` - Debug with Sentry/HoneyBadger integration

### Available Agents

22 specialized agents for:
- Code review (security, performance, architecture)
- Testing (test generation, test running)
- Development (autonomous developer, debugger)
- And more...

See the [full documentation](https://github.com/TechNickAI/ai-coding-config) for complete list.

## Project-Specific Configuration

This project is building:
- **Backend**: Python (FastAPI)
- **Frontend**: React/Next.js (TBD)
- **Database**: PostgreSQL + Vector DB
- **Scraping**: Python (Scrapy/BeautifulSoup)

The `/ai-coding-config` command will detect these and suggest relevant rules.

## Update Configuration

To update to the latest ai-coding-config:

```
/ai-coding-config update
```

## Reference

- **Repository**: https://github.com/TechNickAI/ai-coding-config
- **Local Copy**: `~/.ai_coding_config`
- **Rules Location**: `~/.ai_coding_config/.cursor/rules/`

## Notes

- Rules are loaded on-demand, not copied to the project
- Commands are available once setup is complete
- You can customize which rules to use for this project
- The configuration is project-specific and won't affect other projects

