# 主场景脚本
extends Node2D

# NPC节点引用
@onready var npc_bob: Node2D = $NPCs/NPC_Bob
@onready var npc_alice: Node2D = $NPCs/NPC_Alice
@onready var npc_lily: Node2D = $NPCs/NPC_Lily
@onready var npc_sam: Node2D = $NPCs/NPC_Sam
@onready var npc_kenshin: Node2D = $NPCs/NPC_Kenshin

# API客户端
var api_client: Node = null

# NPC状态更新计时器
var status_update_timer: float = 0.0

func _ready():
	print("[INFO] 主场景初始化")
	
	# 获取API客户端
	api_client = get_node_or_null("/root/APIClient")
	if api_client:
		api_client.npc_status_received.connect(_on_npc_status_received)
		
		# 立即获取一次NPC状态
		api_client.get_npc_status()
	else:
		print("[ERROR] API客户端未找到")

func _process(delta: float):
	# 定时更新NPC状态
	status_update_timer += delta
	if status_update_timer >= Config.NPC_STATUS_UPDATE_INTERVAL:
		status_update_timer = 0.0
		if api_client:
			api_client.get_npc_status()

func _on_npc_status_received(dialogues: Dictionary):
	"""收到NPC状态更新"""
	print("[INFO] 更新NPC状态: ", dialogues)
	
	# 更新各个NPC的对话
	for npc_name in dialogues:
		var dialogue = dialogues[npc_name]
		update_npc_dialogue(npc_name, dialogue)

func update_npc_dialogue(npc_name: String, dialogue: String):
	"""更新指定NPC的对话"""
	var npc_node = get_npc_node(npc_name)
	if npc_node and npc_node.has_method("update_dialogue"):
		npc_node.update_dialogue(dialogue)

func get_npc_node(npc_name: String) -> Node2D:
	"""根据名字获取NPC节点"""
	match npc_name:
		"Bob":
			return npc_bob
		"Alice":
			return npc_alice
		"Lily":
			return npc_lily
		"Sam":
			return npc_sam
		"Kenshin":
			return npc_kenshin
		_:
			return null
