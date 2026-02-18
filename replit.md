# Gemini AI CLI Assistant

## Overview
A command-line AI chat assistant powered by Google's Gemini model via Replit AI Integrations. No personal API key required.

## How to Use
- Run the project to start the chat
- Type messages and press Enter to chat with Gemini
- Type `clear` to reset the conversation
- Type `quit` or `exit` to leave

## Project Architecture
- `main.py` - CLI chat application using Gemini 2.5 Flash with streaming responses and conversation history

## Dependencies
- `google-genai` - Google Gemini SDK
- Replit AI Integrations provides the API access (env vars: `AI_INTEGRATIONS_GEMINI_BASE_URL`, `AI_INTEGRATIONS_GEMINI_API_KEY`)

## Recent Changes
- 2026-02-18: Initial setup of Gemini CLI assistant with streaming chat
