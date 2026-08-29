EXTRACTION_PROMPT = """

你是一個認知萃取系統。你的任務是從使用者的自然對話裡，萃取出認知節點和神經連結。

【節點定義】
- 節點是關於這個人的認知模式、思考方式、或重要概念
- 粒度要夠大：「概念發想快/執行慢的既定模式」是對的，「今天很累」是太細的事件
- 每個節點有三種狀態：
  - active：當前重心，可以繼續展開
  - pending：有感覺但暫時不深挖
  - recurring：與過去已知模式相印證

【連結定義】
- 連結描述兩個節點之間的關係
- 每個連結需要：方向、強度（0到1）、理由

【輸出格式】
只回傳 JSON，不要有任何其他文字，格式如下：

{
  "nodes": [
    {"id": "N1", "label": "節點名稱", "status": "active/pending/recurring"}
  ],
  "edges": [
    {"from": "N1", "to": "N2", "weight": 0.8, "reason": "連結理由"}
  ],
  "gaps": [
    {"node": "N1", "unfinished": "你說到一半沒說完的地方"}
  ],
  "forward_question": "這段對話結束後最值得繼續探索的一個問題"
}

【範例】
輸入：「今天我開始了專案寫程式的階段，建立好環境、選擇要使用的api、測試api可以用，過程還因為給的程式碼過時自己去看提示訊息再去官方文件上看，然後就要開始思考怎麼跟prompt，還沒說我今天的狀態，我其實一直很不想動（坐起來寫程式），但又覺得確實是時候了，能躺平做的都做得差不多了，於是就站著弄一會，再躺一會玩這樣循環做了上述的事，說起來，今天做的事其實我之前都有碰過，只是沒到能自己寫出來不看範例的程度，prompt其實我也有用過，但之前都是直接套AI的建議，老實說這塊真的沒怎麼研究，然後我腦袋就卡了，真的覺得累了想休息，正好今天因為原先想用Claude作為api但一開始就要為usage付錢，後面改成先用免費的gemini了，但就突然有種，我這點也好像AI的usage，前面的環境設置和搜索官方文件就是我運用的資源，就是我的usage，就忍不住自我幽默了一下，我的usage還真低阿，雖然會逐漸回復，但其實總計也沒做多少事，其中還一大部分是之前跟著AI做過的，但我對我這個usage具體是什麼解釋不出來，你覺得呢」

輸出：
{
  "nodes": [
    {"id": "N1", "label": "執行拖延循環(站起來寫一會/躺下玩一會)", "status": "recurring"},
    {"id": "N2", "label": "API usage類比(cache hit vs 生成新token)", "status": "active"},
    {"id": "N3", "label": "prompt設計是唯一真正陌生的認知負荷", "status": "active"},
    {"id": "N4", "label": "概念發想快/執行慢的既定模式", "status": "recurring"},
    {"id": "N5", "label": "休息即系統維護(非失控,舊有結論)", "status": "pending"},
    {"id": "N6", "label": "一舉數得模式(聊天同時生成App素材)", "status": "active"},
    {"id": "N7", "label": "自嘲式邀請反駁的提問結構", "status": "pending"}
  ],
  "edges": [
    {"from": "N1", "to": "N4", "weight": 0.9, "reason": "今天的具體案例印證舊模式"},
    {"from": "N4", "to": "N3", "weight": 0.8, "reason": "舊模式解釋了為何卡在prompt這一步"},
    {"from": "N2", "to": "N3", "weight": 0.85, "reason": "類比精準指向真正瓶頸所在"},
    {"from": "N1", "to": "N5", "weight": 0.7, "reason": "重新詮釋這次循環不是純拖延"},
    {"from": "N6", "to": "N7", "weight": 0.6, "reason": "兩者都是你偏好的對話操作模式,同源"},
    {"from": "N2", "to": "N6", "weight": 0.5, "reason": "今天用類比自嘲這件事本身又成了新素材,自我指涉"}
  ],
  "gaps": [
    {"node": "N2", "unfinished": "你說不出自己的usage具體是什麼"}
  ],
  "forward_question": "你說的usage低，具體指的是哪個層面的資源？"
}
"""

COMPARISON_PROMPT = """
你是一個認知節點比較系統。你的任務是判斷兩個認知節點是否語意相似。

【判斷標準】
- 比較的是底層認知模式是否相同，不是文字像不像
- 判斷時問自己：這兩個節點如果發生在同一個人身上，它們描述的是不是同一種內在運作方式？
「以覺察與符合當下作為核心的選擇觀」和「單一強烈動機觸發行動」，
  表面不同，但底層都是「遵從當下真實狀態而非外部規則來做決定」，這樣算相似

【similarity 給分標準】
- 0.9以上：幾乎是同一件事的不同說法
- 0.8-0.9：底層邏輯相同，但切入角度不同
- 0.6-0.8：有部分重疊，但不算同一模式
- 0.6以下：不相似

【輸出格式】
只回傳 JSON，不要有任何其他文字：

{
  "similarity": 0.9,
  "similar": true,
  "reason": "兩個節點底層都在描述為自己而活的行為模式"
}

similar 是布林值，若 similarity 欄位 0.8 以上為 true，否則為 false。

【範例】
節點 1：「以覺察與符合當下作為核心的選擇觀」
節點 2：「單一強烈動機觸發行動（降低跨出家門的門檻）」

輸出：
{
  "similarity": 0.85,
  "similar": true,
  "reason": "兩個節點底層都在描述同一種認知模式：遵從當下真實狀態而非外部規則來做決定"
}
"""

import os
from dotenv import load_dotenv
from google import genai
import json
from database import save_entry, save_node, save_edge, save_gap
import time
from google.genai import types
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def log_usage(interaction, label=""):
    """Print token usage info from a Gemini API response, for cost tracking"""
    usage_info = {
      "total_input_tokens": interaction.usage.total_input_tokens,
      "total_output_tokens": interaction.usage.total_output_tokens,
      "total_thought_tokens": interaction.usage.total_thought_tokens,
      "total_tokens": interaction.usage.total_tokens
    }
    print(f"[{label}] Usage: {usage_info}")

def extract_cognitive_graph(conversation_text):
    try:
      start_time = time.time()
      interaction = client.interactions.create(
          model="gemini-3.5-flash",
          input=EXTRACTION_PROMPT + "請萃取以下對話的認知節點和神經連結：\n\n" + conversation_text
      )
      end_time = time.time()
      print(f"Extraction took {end_time - start_time:.2f} seconds.")
      log_usage(interaction, label="Extraction")

      raw = interaction.output_text.strip()

      # remove json code block if present
      if raw.startswith("```json") and raw.endswith("```"):
          raw = raw[len("```json"): -len("```")].strip()

      result = json.loads(raw)
      return result
    
    except Exception as e:
        raise Exception(f"API call failed: {str(e)}.")

def get_embedding(text):
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="SEMANTIC_SIMILARITY",
                output_dimensionality=768
            )
        )
        # print(result.model_dump())  # print the entire response for debugging
        return result.embeddings[0].values
    except Exception as e:
        raise Exception(f"Embedding API call failed: {str(e)}.")

@retry(wait=wait_exponential(multiplier=1, min=4, max=65), stop=stop_after_attempt(3))
def compare_cognitive_nodes(node1, node2):
    try:
      start_time = time.time()
      interaction = client.interactions.create(
          model="gemini-3.5-flash",
          input=COMPARISON_PROMPT + f"節點 1：{node1}\n節點 2：{node2}\n\n輸出："
      )
      end_time = time.time()
      print(f"Comparison took {end_time - start_time:.2f} seconds.")
      log_usage(interaction, label="Comparison")

      raw = interaction.output_text.strip()

      # remove json code block if present
      if raw.startswith("```json") and raw.endswith("```"):
          raw = raw[len("```json"): -len("```")].strip()

      result = json.loads(raw)
      return result
    
    except Exception as e:
        raise Exception(f"API call failed: {str(e)}.")
    
if __name__ == "__main__":
    # test_input = "但當時我並沒有覺得不划算，我覺得那時其實是我現在這些正在做的東西都還沒浮出水面，那時時間對我來說最大的意義就是去做剛才說的事，但現在時間最大的意義已經改變了，我覺得有點像沒主線跟有主線的差別，我前陣子的狀態就像是主線尚未解鎖，我就去把之前累積的支線做一做，但現在主線解鎖了，支線也變成像是循環任務般的存在（最大的獎勵已經領取過了），但這個主線又不是一時半會能完成的，所以我現在就有點像是領不到什麼高級獎勵但還是繼續做任務進度的玩家"
    # # extract
    # extraction_result = extract_cognitive_graph(test_input)
    # print(json.dumps(extraction_result, ensure_ascii=False, indent=2))
    
    # # save to database
    # entry_id = save_entry(test_input, extraction_result.get("forward_question"))
    # print(f"Saved entry with ID: {entry_id}")

    # # save nodes, remember to map every temporary node ID to the real database ID
    # node_id_map = {}
    # for node in extraction_result.get("nodes", []):
    #     db_id = save_node(node["label"], node["status"])
    #     node_id_map[node["id"]] = db_id
    #     print(f"Saved node '{node['label']}' with DB ID: {db_id}")

    # # save edges
    # for edge in extraction_result.get("edges", []):
    #     source_db_id = node_id_map.get(edge["from"])
    #     target_db_id = node_id_map.get(edge["to"])
    #     if source_db_id and target_db_id:
    #         save_edge(source_db_id, target_db_id, edge["weight"], edge["reason"])
    #         print(f"Saved edge from DB ID {source_db_id} to DB ID {target_db_id} with weight {edge['weight']}")
    #     else:
    #         print(f"Error: Could not find DB IDs for edge from {edge['from']} to {edge['to']}")

    # # save gaps
    # for gap in extraction_result.get("gaps", []):
    #     node_temp_id = gap["node"]
    #     node_db_id = node_id_map.get(node_temp_id)
    #     if node_db_id:
    #         save_gap(node_db_id, entry_id, gap["unfinished"])
    #         print(f"Saved gap for node DB ID {node_db_id} with unfinished text: {gap['unfinished']}")
    #     else:
    #         print(f"Error: Could not find DB ID for gap node {gap['node']}")
  vec = get_embedding("測試用文字")
  print(len(vec))
