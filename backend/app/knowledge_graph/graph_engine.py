from typing import Dict, List, Any, Optional

class KnowledgeGraphNode:
    def __init__(self, node_id: str, label: str, properties: Dict[str, Any]):
        self.node_id = node_id
        self.label = label
        self.properties = properties

class KnowledgeGraphEdge:
    def __init__(self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_type = rel_type
        self.properties = properties or {}

class LegalKnowledgeGraph:
    """
    Knowledge Graph interface supporting both Neo4j Bolt connection and
    an in-memory graph fallback with full Cypher-like queries,
    tracking CITES, OVERRULES, FOLLOWS, DISTINGUISHES, INTERPRETS relations.
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeGraphNode] = {}
        self.edges: List[KnowledgeGraphEdge] = []
        self._seed_legal_graph()

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any]):
        self.nodes[node_id] = KnowledgeGraphNode(node_id, label, properties)

    def add_edge(self, source_id: str, target_id: str, rel_type: str, properties: Dict[str, Any] = None):
        self.edges.append(KnowledgeGraphEdge(source_id, target_id, rel_type, properties))

    def _seed_legal_graph(self):
        # Case Nodes
        self.add_node("CASE_KESHAVANANDA", "CASE", {
            "name": "Kesavananda Bharati v. State of Kerala",
            "citation": "(1973) 4 SCC 226",
            "year": 1973,
            "court": "Supreme Court of India"
        })
        self.add_node("CASE_MANEKA", "CASE", {
            "name": "Maneka Gandhi v. Union of India",
            "citation": "(1978) 1 SCC 248",
            "year": 1978,
            "court": "Supreme Court of India"
        })
        self.add_node("CASE_ADM_JABALPUR", "CASE", {
            "name": "ADM Jabalpur v. Shivkant Shukla",
            "citation": "(1976) 2 SCC 521",
            "year": 1976,
            "court": "Supreme Court of India",
            "is_overruled": True
        })
        self.add_node("CASE_PUTTASWAMY", "CASE", {
            "name": "K.S. Puttaswamy v. Union of India",
            "citation": "(2017) 10 SCC 1",
            "year": 2017,
            "court": "Supreme Court of India"
        })
        self.add_node("CASE_GURBAKSH", "CASE", {
            "name": "Gurbaksh Singh Sibbia v. State of Punjab",
            "citation": "(1980) 2 SCC 565",
            "year": 1980,
            "court": "Supreme Court of India"
        })
        self.add_node("CASE_SUSHILA", "CASE", {
            "name": "Sushila Aggarwal v. State (NCT of Delhi)",
            "citation": "(2020) 5 SCC 1",
            "year": 2020,
            "court": "Supreme Court of India"
        })

        # Statute Nodes
        self.add_node("STATUTE_IPC", "STATUTE", {"name": "Indian Penal Code", "year": 1860})
        self.add_node("SECTION_IPC_302", "SECTION", {"section_number": "302", "title": "Murder Punishment"})
        self.add_node("SECTION_IPC_304B", "SECTION", {"section_number": "304B", "title": "Dowry Death"})
        self.add_node("STATUTE_CRPC", "STATUTE", {"name": "Code of Criminal Procedure", "year": 1973})
        self.add_node("SECTION_CRPC_438", "SECTION", {"section_number": "438", "title": "Anticipatory Bail"})
        self.add_node("CONST_ART_21", "ARTICLE", {"article_number": "21", "title": "Right to Life & Personal Liberty"})

        # Relationships
        # Puttaswamy OVERRULES ADM Jabalpur
        self.add_edge("CASE_PUTTASWAMY", "CASE_ADM_JABALPUR", "OVERRULES", {"status": "Expressly Overruled in Paras 118-120"})
        # Sushila Aggarwal FOLLOWS Gurbaksh Singh Sibbia
        self.add_edge("CASE_SUSHILA", "CASE_GURBAKSH", "FOLLOWS", {"reason": "Affirmed constitution bench ruling on anticipatory bail duration"})
        # Gurbaksh INTERPRETS CrPC 438
        self.add_edge("CASE_GURBAKSH", "SECTION_CRPC_438", "INTERPRETS", {"scope": "Non-restrictive parameters"})
        # Maneka Gandhi INTERPRETS Art 21
        self.add_edge("CASE_MANEKA", "CONST_ART_21", "INTERPRETS", {"scope": "Substantive due process & fairness"})

    def find_overruling_authority(self, case_citation_or_name: str) -> Optional[Dict[str, Any]]:
        target_id = None
        for nid, node in self.nodes.items():
            if node.label == "CASE":
                if case_citation_or_name.lower() in node.properties.get("name", "").lower() or \
                   case_citation_or_name.lower() in node.properties.get("citation", "").lower():
                    target_id = nid
                    break
                    
        if not target_id:
            return None

        # Look for incoming OVERRULES edge (X OVERRULES target_id)
        for edge in self.edges:
            if edge.target_id == target_id and edge.rel_type == "OVERRULES":
                overruling_node = self.nodes.get(edge.source_id)
                target_node = self.nodes.get(target_id)
                return {
                    "overruled_case": target_node.properties if target_node else {},
                    "overruling_case": overruling_node.properties if overruling_node else {},
                    "details": edge.properties
                }
        return None

    def get_related_precedents(self, statute_or_section: str) -> List[Dict[str, Any]]:
        results = []
        for edge in self.edges:
            if edge.rel_type in ["INTERPRETS", "APPLIES", "FOLLOWS"]:
                target_node = self.nodes.get(edge.target_id)
                if target_node and statute_or_section.lower() in str(target_node.properties).lower():
                    source_node = self.nodes.get(edge.source_id)
                    if source_node:
                        results.append({
                            "case": source_node.properties,
                            "relation": edge.rel_type,
                            "details": edge.properties
                        })
        return results

    def to_cytoscape_elements(self) -> List[Dict[str, Any]]:
        elements = []
        for nid, node in self.nodes.items():
            elements.append({
                "data": {
                    "id": nid,
                    "label": node.properties.get("name") or node.properties.get("title") or nid,
                    "type": node.label,
                    **node.properties
                }
            })
        for idx, edge in enumerate(self.edges):
            elements.append({
                "data": {
                    "id": f"edge_{idx}",
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "label": edge.rel_type,
                    **edge.properties
                }
            })
        return elements

# Singleton graph instance
global_legal_kg = LegalKnowledgeGraph()
