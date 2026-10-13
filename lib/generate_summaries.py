# Use ollama to generate summaries from rpg chat logs
try:
    from lib.ollama_api import OllamaAPI
    from lib.custom_logger import get_custom_logger
except ImportError:
    from ollama_api import OllamaAPI
    from custom_logger import get_custom_logger

logger = get_custom_logger(__file__, __name__, True, False, True)


#MODEL = "ALIENTELLIGENCE/roleplaymaster:latest"
# MODEL = "gemma3:4b"
MODEL = "gemma4:e4b"
class SummaryGenerator:
    def __init__(self, model=MODEL):
        self.api = OllamaAPI()
        self.model = model
        self.chatlog = None
        self.summaries = []
        self.num_blocks = 1 # Number of blocks to include in each summary prompt (e.g., 1 for block-by-block, 2 for pairs of blocks, etc.)
    def load_chat_log(self, filename):
        with open(filename, "r", encoding="UTF-8") as f:
            self.chatlog = f.read()
        logger.info(f"Chat log loaded from {filename}")

    def get_chatlog_block(self):
        """Chatlogs are in markdown with H2 titles for each block.
        Usually in a format:
        ## 1 🗨️ USER: and
        ## 2 🤖 ASSISTANT:
        """
        self.chatlog_blocks = []
        if not self.chatlog:
            raise ValueError("Chatlog not loaded. Call load_chat_log() first.")
        # Split by H2 titles in specific format
        blocks = self.chatlog.split("## ")
        logger.info(f"Found {len(blocks)-1} blocks in chat log")
        for block in blocks:
            if block.strip():
                # Check block starts with expected format, with variable index
                process_block = (block.split(" ")[0].strip(":").isdigit()
                    and block.split(" ")[1].strip().strip(":") in ["🗨️", "🤖", "User", "LLM"])
                # logger.debug(f'--{block.split(" ")[1].strip().strip(":")}--')
                if (process_block):
                    yield block.strip()

    def process_blocks(self, prompt, postfix, max=None):
        index = 0
        proc_blocks= []
        for block in self.get_chatlog_block():
            proc_blocks.append(block)
            logger.info(f"Processing block {index}...")
            if len(proc_blocks) >= self.num_blocks:
                block = "\n".join(proc_blocks) # hox - replaced block from get_chatlog_block temporarily
                summary = self.api.chat(self.model, f"{prompt}{block}{postfix}", stream=True)
                result = [s for s in summary]
                if isinstance(result[0], tuple):
                    assert len(result[0]) == 2, f"Expected tuple of (message, response), got {type(result[0])}"
                    result = "".join(r for r in result[0][1])
                logger.info(result)
                yield str(result)
                proc_blocks = []
            index += 1
            if max and index >= max - 1:
                break

    def generate_summaries(self, max=None):
        logger.info("Generating summaries...")
        prompt = """Summarize the following chat log block in 1-2 sentences.
        Focus on key events, decisions, and outcomes.
        Be concise but informative.\n # Block:\n"""

        postfix = """\n\n---\n End block. Provide summary as requested.
        \n"""
        for result in self.process_blocks(prompt, postfix):
            self.summaries.append(str(result))

    def generate_better_summaries(self, max=None):
        logger.info("Generating summaries...")
        prompt = """Summarize the following chat log block in 1-2 sentences.
        Focus on key events, decisions, and outcomes.
        Be concise but informative.\n # Block:\n"""

        postfix = """\n\n---\n End block. Provide summary as requested.
        \n"""
        for result in self.process_blocks(prompt, postfix):
            self.summaries.append(str(result))

    def final_processing(self):
        logger.info("Final processing of summaries...")
        prompt = """Given the following summaries of chat log blocks, synthesize a final summary that captures the overall narrative, key developments, and character arcs. Be concise but comprehensive.\n # Summaries:\n"""

        postfix = """\n\n---\n End summaries. Provide final summary as requested.
        \n"""
        block = "\n".join(self.summaries)
        final_summary = self.api.chat(self.model, f"{prompt}{block}{postfix}", stream=True)
        logger.info(f"Final summary:\n{final_summary}")
        return final_summary


    def collect_feats(self):
        logger.info("Collecting feats...")
        prompt = """Extract feats of power, abilities, or other skills from the
        following chat log block. Focus on unique or significant feats that are
        relevant to the characters or story. Be concise but informative.
        Ignore trivial abilities or artistic embellishments. \n # Block:\n"""

        postfix = """\n\n---\n End block. Provide feats as requested.
        If none are displayed, that is okay, we'll move on.\n"""
        for result in self.process_blocks(prompt, postfix):
            self.summaries.append(str(result))


    def extract_blocks_by_tag(self, tags):
        """Extract blocks that contain a specific tag (e.g., "USER" or "ASSISTANT")"""
        if isinstance(tags, str):
            tags = [tags]

        for block in self.get_chatlog_block():
            if any (f"{tag}:" in block for tag in tags):
                yield block.strip()


def save_extracted_blocks(blocks, filename):
    with open(filename, "w", encoding="UTF-8") as f:
        for idx, block in enumerate(blocks, start=1):
            f.write(f"## {idx} {block}\n\n---\n\n")

if __name__ == "__main__":

    # Optionally take in a chat log file as an argument, or default to "example_chatlog.md"
    import sys
    if len(sys.argv) > 1:
        chatlog_file = sys.argv[1]
    else:
        chatlog_file = "example_chatlog.md"

    # Take in output file name as an argument, or default to "summaries.txt"
    if len(sys.argv) > 2:
        output_file = sys.argv[2]


    sg = SummaryGenerator()


    print("Models available:")
    api = OllamaAPI()
    models = api.list_models()
    for model in models["models"]:
        logger.info(model["name"])
    # model = "gemma4:e4b"
    #model = "nemotron-3-nano:4b"
    model = "cryptidbleh/gemma4-claude-opus-4.6:latest"
    # model = "ducquoc/gpt-oss-sonnet:latest"
    generator = SummaryGenerator(model=model)
    generator.load_chat_log(chatlog_file)

    # # Parse function args
    # functions = ["generate_summaries", "collect_feats"]
    # print (sys.argv)
    # if len(sys.argv) > 3:
    #     function_arg = sys.argv[3] or "generate_summaries"
    #     if function_arg not in generator.__dict__:
    #         function_arg = "generate_summaries"
    # else:
    #     output_file = "summaries.txt"


    sg.load_chat_log(chatlog_file)

    #extracted = sg.extract_blocks_by_tag("🗨️ USER")
    extracted = sg.extract_blocks_by_tag("User:")
    save_extracted_blocks(extracted, "user_blocks.md")
    extracted = sg.extract_blocks_by_tag("🤖 ASSISTANT")
    save_extracted_blocks(extracted, "assistant_blocks.md")
    generator.num_blocks = 10
    generator.generate_summaries()
    # generator.collect_feats()
    final = generator.final_processing()
    # prompt = """Summarize the feats from following text block."""
    # postfix = """\n\n---\n End block. Provide summary as requested."""
    # block = "\n".join(generator.summaries)
    # final_summary = generator.api.chat(generator.model, f"{prompt}{block}{postfix}", stream=True)
    # generator.__dict__[function_arg]()
    # write to file with indexes
    with open(output_file, "w", encoding="UTF-8") as f:
        for idx, summary in enumerate(generator.summaries, start=1):
            summary_text = "".join(summary)
            f.write(f"\n{idx}. {summary_text}\n")
        # f.write(f"\nFinal summary:\n{final_summary}\n")
        f.write(f"\nFinal summary:\n{final}\n")
    logger.info(f"Summaries written to {output_file}")