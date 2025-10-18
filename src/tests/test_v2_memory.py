import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from v2_llm_graph.src.memory.vector_memory import VectorMemory

@pytest.fixture
def mock_chroma_client():
    with patch('chromadb.PersistentClient') as mock_client:
        # Create a mock collection
        mock_collection = MagicMock()
        # Setup the client to return our mock collection
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        yield mock_client.return_value, mock_collection

def test_vector_memory_initialization(mock_chroma_client):
    """
    Test that VectorMemory initializes correctly with ChromaDB.
    """
    mock_client, mock_collection = mock_chroma_client
    
    # Act
    memory = VectorMemory(db_path="test/path")
    
    # Assert
    mock_client.get_or_create_collection.assert_called_once_with(
        name="quant_apprentice_memory"
    )

def test_add_analysis_success(mock_chroma_client):
    """
    Test successful addition of an analysis report to memory.
    """
    mock_client, mock_collection = mock_chroma_client
    memory = VectorMemory()
    
    # Act
    memory.add_analysis("AAPL", "Test analysis report")
    
    # Assert
    mock_collection.add.assert_called_once()
    # Verify the document was added with correct metadata
    call_args = mock_collection.add.call_args[1]
    assert len(call_args['documents']) == 1
    assert call_args['documents'][0] == "Test analysis report"
    assert call_args['metadatas'][0]['ticker'] == "AAPL"
    assert 'date' in call_args['metadatas'][0]

def test_add_analysis_error(mock_chroma_client):
    """
    Test error handling when adding an analysis fails.
    """
    mock_client, mock_collection = mock_chroma_client
    mock_collection.add.side_effect = Exception("Database error")
    memory = VectorMemory()
    
    # Act
    memory.add_analysis("AAPL", "Test analysis report")
    
    # Assert - verify it handles the error gracefully
    mock_collection.add.assert_called_once()

def test_query_memory_success(mock_chroma_client):
    """
    Test successful memory query.
    """
    mock_client, mock_collection = mock_chroma_client
    memory = VectorMemory()
    
    # Setup mock response
    mock_collection.query.return_value = {
        'documents': [['Test analysis 1', 'Test analysis 2']]
    }
    
    # Act
    results = memory.query_memory("test query", n_results=2)
    
    # Assert
    assert len(results) == 2
    assert results[0] == 'Test analysis 1'
    assert results[1] == 'Test analysis 2'
    mock_collection.query.assert_called_once_with(
        query_texts=["test query"],
        n_results=2
    )

def test_query_memory_error(mock_chroma_client):
    """
    Test error handling when querying memory fails.
    """
    mock_client, mock_collection = mock_chroma_client
    memory = VectorMemory()
    
    # Setup mock to raise an exception
    mock_collection.query.side_effect = Exception("Query error")
    
    # Act
    results = memory.query_memory("test query")
    
    # Assert
    assert results == []
    mock_collection.query.assert_called_once()