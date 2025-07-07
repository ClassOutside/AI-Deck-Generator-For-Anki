<p align="center">
  <img src="https://github.com/user-attachments/assets/5ea763c9-950f-4cce-a5fb-9902a3a5f286" alt="Deck Generator Logo" width="200" style="border-radius: 50%;" />
</p>

<h1 align="center">AI Deck Generator for Anki</h1>

<p align="center"><i>Japanese-to-English note cards translated by AI and organized into a structured deck for Anki import.</i></p>

---

## Disclaimer

- **API Key & Billing:** You are responsible for any costs incurred through use of your OpenAI API key. Be mindful of usage, as charges are billed directly to the account associated with the key you provide.

- **Encrypted Key Storage:** Your API key is encrypted, and stored with the salt and IV in `keys.py`. **Do not** commit or share this file with its encrypted contents.  

- **Translation Accuracy:** This tool uses AI to generate translations. While often accurate, AI‑generated content may occasionally include errors, mistranslations, or unexpected results.

- **Audio Output Accuracy:** If audio generation is used, please note that pronunciation accuracy may vary. In Japanese, many kanji have multiple possible readings depending on context. The tools used may not always select the correct pronunciation or may introduce errors during synthesis.

---

## Steps to Run Locally

🎥 **Video Tutorial (Coming Soon):** [Watch on YouTube]()

1. **Download and prepare VOICEVOX** 

2. **Download and unzip the AI Deck Generator for Anki**  

3. **Run the executable (`.exe`) file**  

4. **Read the Terms and Conditions**  

5. **If you agree, proceed to the settings menu**
   - **5a.** Select an output directory  
   - **5b.** Select the location of the VOICEVOX executable  
   - **5c.** Input your OpenAI API key  
   - **5d.** Create a PIN – this will be required to initiate deck generation. API calls will not be made without the correct PIN.

6. **Exit the application**, then run the `.exe` again for the changes to take effect.

7. **Fill in the fields for translation**
   - **7a.** Provide your PIN  
   - **7b.** Title your Anki deck  
   - **7c.** Input the Japanese text you want translated

8. **Click the “Generate” button**  
   - The application will process the input, generate translations, and build the Anki deck.

9. **Import into Anki**

---

<p align="center">
  <img src="https://github.com/user-attachments/assets/0245c54a-e883-4317-8d6e-5c7243b2fa72" alt="Class-Outside Logo" width="200" style="border-radius: 50%;" />
</p>

<h2 align="center">Class Outside</h2>

<p align="center">
  ☕️ Do you like my work? Consider leaving a tip or supporting me through <a href="https://ko-fi.com/classoutside" target="_blank">Ko-fi</a>.
</p>

---

## Overview

The AI Deck Generator for Anki assists users in converting Japanese text into structured, study-ready Anki flashcards. By supplying an OpenAI API key, users can leverage AI to:

- Break down input text into individual sentences
- Contextually translate sentences into English
- Identify and explain unique vocabulary and kanji

The result is an organized Anki deck that can be directly imported into the Anki app.

**Note:** Use of this tool requires a valid OpenAI API key. Charges will apply to the API key owner based on usage.

---

## Deck structured

- The deck is broken up into two sections, Japanese to English, and English to Japanese. 
- Both sections include note cards for full sentences, words, and kanji.

<p align="center">
  <img src="https://github.com/user-attachments/assets/53290191-ed52-4a8f-ab59-67c5a353f060" alt="Anki Deck Structure" width="200" style="border-radius: 50%;" />
</p>

---

## Card format

- The note cards formats vary slightly based on section.
- Each should include:
    - Japanese text
    - Romaji pronunciation
    - Japanese audio
    - English translation

EX: Japanese to English, Front Side
- Kanji
- mp3 audio example

<p align="center">
  <img src="https://github.com/user-attachments/assets/0b6d80b4-4151-499c-acba-c55c42234934" alt="Card Front Format" width="200" style="border-radius: 50%;" />
</p>

EX: Japanese to English, Back Side
- English Translation
- Romaji pronunciation

<p align="center">
  <img src="https://github.com/user-attachments/assets/d11e0786-fec1-44f9-b071-de6888273db5" alt="Card Front Format" width="200" style="border-radius: 50%;" />
</p>

---

## Dependencies

### Text Translations: ChatGPT
- ChatGPT is used to break out words and kanji from Japanese sentences and provide contextual translations for all components.
- As of **July 2025**, the **gpt-4o-mini** model was used. This model demonstrated accurate and consistent results in internal testing.

### Audio Output: VOICEVOX
- [VOICEVOX](https://voicevox.hiroshiba.jp/) is used as the text-to-speech engine for generating Japanese audio from the processed text.
- VOICEVOX must be **downloaded and installed separately**.
- You can download VOICEVOX and find installation instructions at the official site: [VOICEVOX Downloads](https://voicevox.hiroshiba.jp/)

## Estimating Costs

This tool requires you to use your own OpenAI API key. **You, as the owner of the API key, are fully responsible for any charges incurred.** The software creator assumes no liability for API usage, billing, or resulting costs.

Up-to-date model pricing is maintained by OpenAI and can be reviewed here:  
🔗 [OpenAI Pricing Documentation](https://platform.openai.com/docs/pricing)

As of **July 2025**, this tool uses the **gpt-4o-mini** model by default, unless manually changed.

### Budgeting and Monitoring Usage

OpenAI provides features that may help you manage costs more safely:

- You can **set spending limits or hard usage caps** in your [OpenAI account settings](https://platform.openai.com/account/billing/limits) to help avoid unexpected charges.
- You can also **review detailed usage history** and see how many tokens you've consumed in your [usage dashboard](https://platform.openai.com/account/usage).

### Estimating Token Costs

To roughly estimate the cost of using this tool with your text:

1. **Estimate Input Tokens**
   - Visit the [OpenAI Tokenizer Tool](https://platform.openai.com/tokenizer)
   - Select the **model tab** (currently `gpt-4o-mini`)
   - Paste in the **prompt** (found in this repository)
   - Then, paste in the **text you wish to translate**
   - This will give you an approximate input token count

2. **Estimate Output Tokens**
   - Log in to a standard [ChatGPT](https://chat.openai.com) account
   - Start a new chat and paste in the prompt from `prompt.txt`, along with your input text
   - Copy the resulting output from ChatGPT
   - Paste that output into the [tokenizer](https://platform.openai.com/tokenizer) to get an output token estimate

3. **Calculate Costs**
   - Once you have both input and output token counts, consult the [pricing page](https://platform.openai.com/docs/pricing) to determine the cost per million tokens for both input and output.
   - Multiply your token counts accordingly to estimate cost.

> ⚠️ Please note: Token counts and output length may vary from test runs due to changes in model behavior or structure. Estimates are not guarantees.

---

## Affiliations

This project is an independent creation and is **not affiliated with** or endorsed by:

- Anki or the Anki development team  
- VOICEVOX or its developers  
- OpenAI or its affiliates  

---

### THIRD_PARTY_LICENSES

**Feather Icons**  
Copyright (c) 2013–2023 Cole Bemis  
License: [MIT License](https://github.com/feathericons/feather)

MIT License:
> Permission is hereby granted, free of charge, to any person obtaining a copy  
> of this software and associated documentation files (the "Software"), to deal  
> in the Software without restriction, including without limitation the rights  
> to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
> copies of the Software, and to permit persons to whom the Software is  
> furnished to do so, subject to the following conditions:  
>
> The above copyright notice and this permission notice shall be included in all  
> copies or substantial portions of the Software.  
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
> IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
> FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
> AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
> LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
> OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
> SOFTWARE.
