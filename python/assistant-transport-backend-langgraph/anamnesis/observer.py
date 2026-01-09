"""
Observer Module - Processing Observation Data
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Observer:
    """
    Represents an observation point in the Anamnesis Engine.
    Processes data streams to facilitate 'unforgetting'.
    """

    def __init__(self, observer_id: str):
        self.observer_id = observer_id
        self.memory_buffer: List[Dict[str, Any]] = []

    def observe(self, data: Dict[str, Any]):
        """Records an observation."""
        timestamped_data = {
            "timestamp": datetime.now().isoformat(),
            "observer_id": self.observer_id,
            **data
        }
        self.memory_buffer.append(timestamped_data)
        logger.info(f"Observer {self.observer_id} recorded event.")

    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyzes recorded observations to find patterns using Pandas.
        """
        if not HAS_PANDAS or not self.memory_buffer:
            return {"status": "insufficient_data_or_tools"}

        df = pd.DataFrame(self.memory_buffer)
        
        # Simple analysis: Count of event types if 'type' field exists
        analysis_result = {}
        if 'type' in df.columns:
            analysis_result['type_counts'] = df['type'].value_counts().to_dict()
        
        analysis_result['total_observations'] = len(df)
        analysis_result['time_span_start'] = df['timestamp'].min()
        analysis_result['time_span_end'] = df['timestamp'].max()

        return analysis_result

    def clear_memory(self):
        """Clears the local memory buffer."""
        self.memory_buffer = []
