"""
Analyzer for passive voice and agency erasure patterns
"""

from typing import Dict, List, Tuple
import spacy


class AgencyAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not installed
            self.nlp = None

        # Violence-related terms that might be passive
        self.violence_terms = {
            "killed",
            "murdered",
            "massacred",
            "executed",
            "slaughtered",
            "tortured",
            "beaten",
            "arrested",
            "imprisoned",
            "detained",
            "suppressed",
            "oppressed",
            "exploited",
            "enslaved",
            "displaced",
            "attacked",
            "invaded",
            "conquered",
            "colonized",
            "occupied",
            "destroyed",
            "burned",
            "raided",
            "pillaged",
            "plundered",
        }

        # Resistance terms (often active voice for natives)
        self.resistance_terms = {
            "resisted",
            "fought",
            "rebelled",
            "revolted",
            "uprising",
            "attacked",
            "defended",
            "protested",
            "opposed",
            "challenged",
        }

        # Nominalization patterns (verbs turned to nouns)
        self.nominalization_patterns = {
            "violence occurred": "violence",
            "conflict arose": "conflict",
            "resistance happened": "resistance",
            "oppression took place": "oppression",
            "exploitation existed": "exploitation",
            "massacre took place": "massacre",
            "rebellion broke out": "rebellion",
        }

        # Colonial actors
        self.colonial_actors = {
            "british",
            "french",
            "spanish",
            "portuguese",
            "dutch",
            "belgian",
            "italian",
            "german",
            "colonial",
            "european",
            "empire",
            "colonial forces",
            "troops",
            "soldiers",
            "administration",
            "authorities",
            "government",
            "colonizers",
            "settlers",
            "colonial power",
        }

        # Native actors
        self.native_actors = {
            "natives",
            "indigenous",
            "local",
            "tribal",
            "natives",
            "resistance",
            "rebels",
            "fighters",
            "population",
            "people",
            "inhabitants",
            "villagers",
            "community",
        }

    def analyze_agency(self, text: str) -> Dict:
        """
        Detect patterns of agency erasure through passive voice
        """
        patterns = {
            "passive_violence": [],
            "active_resistance": [],
            "nominalization": [],
            "agent_deletion": [],
        }

        statistics = {
            "total_violence_references": 0,
            "passive_violence_pct": 0.0,
            "agent_deletion_pct": 0.0,
            "native_active_violence_pct": 0.0,
        }

        if not self.nlp:
            return {"patterns": patterns, "statistics": statistics}

        doc = self.nlp(text)

        # Analyze sentences
        violence_count = 0
        passive_violence_count = 0
        agent_deletion_count = 0
        native_active_violence_count = 0

        for sent in doc.sents:
            sent_text = sent.text.strip()

            # Check for violence terms
            has_violence = any(
                term in sent_text.lower() for term in self.violence_terms
            )
            has_resistance = any(
                term in sent_text.lower() for term in self.resistance_terms
            )

            if has_violence:
                violence_count += 1

                # Check if passive voice
                is_passive, actor = self._is_passive_construction(sent)

                if is_passive:
                    passive_violence_count += 1
                    patterns["passive_violence"].append(
                        {"text": sent_text, "actor": actor}
                    )

                    if not actor:
                        agent_deletion_count += 1
                        patterns["agent_deletion"].append(
                            {"text": sent_text, "type": "violence"}
                        )

                # Check if native is active subject committing violence
                if self._has_native_active_violence(sent):
                    native_active_violence_count += 1

            if has_resistance:
                # Check if active voice for resistance
                is_active = self._is_active_construction(sent)
                if is_active:
                    patterns["active_resistance"].append({"text": sent_text})

            # Check for nominalization
            nominalizations = self._detect_nominalization(sent_text)
            if nominalizations:
                patterns["nominalization"].extend(
                    [{"text": sent_text, "pattern": nom} for nom in nominalizations]
                )

        # Calculate statistics
        statistics["total_violence_references"] = violence_count
        if violence_count > 0:
            statistics["passive_violence_pct"] = (
                passive_violence_count / violence_count
            ) * 100
            statistics["agent_deletion_pct"] = (
                agent_deletion_count / violence_count
            ) * 100
            statistics["native_active_violence_pct"] = (
                native_active_violence_count / violence_count
            ) * 100

        return {"patterns": patterns, "statistics": statistics}

    def _is_passive_construction(self, sent) -> Tuple[bool, str]:
        """
        Check if sentence uses passive voice
        Returns (is_passive, actor_if_found)
        """
        actor = None
        is_passive = False

        for token in sent:
            # Check for passive auxiliary + past participle
            if token.dep_ == "auxpass":
                is_passive = True

                # Look for agent in "by" phrase
                for child in token.head.children:
                    if child.dep_ == "agent" or (
                        child.dep_ == "prep" and child.text.lower() == "by"
                    ):
                        for subchild in child.children:
                            if subchild.dep_ == "pobj":
                                actor = subchild.text
                                break

        return is_passive, actor

    def _is_active_construction(self, sent) -> bool:
        """
        Check if sentence uses active voice with clear subject
        """
        has_subject = False
        has_verb = False

        for token in sent:
            if token.dep_ in ["nsubj", "nsubjpass"]:
                has_subject = True
            if token.pos_ == "VERB" and token.dep_ not in ["auxpass"]:
                has_verb = True

        return has_subject and has_verb

    def _has_native_active_violence(self, sent) -> bool:
        """
        Check if native actors are portrayed as active agents of violence
        """
        sent_text = sent.text.lower()

        has_native = any(actor in sent_text for actor in self.native_actors)
        has_violence = any(term in sent_text for term in self.violence_terms)

        if not (has_native and has_violence):
            return False

        # Check if native is subject of violence verb
        for token in sent:
            if token.dep_ in ["nsubj"] and any(
                actor in token.text.lower() for actor in self.native_actors
            ):
                # Check if this subject is doing violence
                head = token.head
                if head.pos_ == "VERB" and any(
                    term in head.text.lower() for term in self.violence_terms
                ):
                    return True

        return False

    def _detect_nominalization(self, text: str) -> List[str]:
        """
        Detect nominalization patterns that obscure agency
        """
        found = []
        text_lower = text.lower()

        for pattern, noun in self.nominalization_patterns.items():
            if pattern in text_lower or noun in text_lower:
                found.append(pattern)

        return found
