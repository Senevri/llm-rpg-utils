import tiktoken
import spacy

# Load the spaCy model
# nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("en_core_web_sm")


# Conversation
encoding = tiktoken.get_encoding("cl100k_base")


class Conversation:
    def __init__(self):
        self.blocks = []
        self.current_block = None

    def append(self, block):
        entities = self.analyze_text(block.text)
        block.entities = entities
        self.blocks.append(block)

    def check_text_in_blocks(self, text):
        for block in self.blocks:
            if text in block.text:
                return True
        return False

    def analyze_text(self, text):
        # print(text)
        doc = nlp(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities

    def find_blocks_with_entities(self, entities: list):
        for block in self.blocks:
            for entity in entities:
                if entity in block.entities:
                    yield block


class ConversationBlock:
    def __init__(self, name, text, index=-1):
        self.name = name
        self.text = text
        self.tokens = None
        self.index = index
        self.options = []
        self.entities = []

    def tokenize_text(self):
        self.tokens = encoding.encode(self.text)


if __name__ == "__main__":
    sample_texts = [
        ("start", "This is the start of the conversation"),
        ("middle", "This is the middle of the conversation"),
        ("end", "This is the end of the conversation"),
        (
            "fred",
            "It seems like Fred is a nice guy, except for his habit of being rude when annoyed",
        ),
        ("fred", "I wonder if I should invite Fred?"),
    ]

    conversation = Conversation()

    # for text in sample_texts:
    #     conversation.append(ConversationBlock(*text))

    with open("hellsing_content.txt", "r", encoding="UTF-8") as file:
        data = file.read()
        blocks = data.split("---")

    for block in blocks:
        conversation.append(ConversationBlock("chat", block, 0))

    tokens = 0
    for block in conversation.blocks:
        block.tokenize_text()
        tokens = tokens + len(block.tokens)

        # print(encoding.decode(block.tokens))
        # print(block.entities)
    test_string = "Now where is fucking Alucard?"
    entities = conversation.analyze_text(test_string)
    print(entities)
    blocks = conversation.find_blocks_with_entities(entities)
    for block in blocks:
        print(block.text)
    print(f"number of tokens: {tokens}")
