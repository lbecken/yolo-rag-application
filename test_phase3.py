#!/usr/bin/env python3
"""
Phase 3 Testing Script
Tests the /ingest endpoint and verifies database records
"""

import requests
import sys
import time
from pathlib import Path
import subprocess
import json

# Configuration
PYTHON_SERVICE_URL = "http://localhost:8000"
INGEST_ENDPOINT = f"{PYTHON_SERVICE_URL}/ingest"
HEALTH_ENDPOINT = f"{PYTHON_SERVICE_URL}/health"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def check_service_health():
    """Check if the Python service is running and healthy"""
    print_section("1. Health Check")

    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        response.raise_for_status()
        health_data = response.json()

        print("✓ Python service is healthy")
        print(f"  Service: {health_data.get('service')}")
        print(f"  Version: {health_data.get('version')}")
        print(f"  Status: {health_data.get('status')}")
        return True

    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Python service")
        print(f"  Make sure the service is running at {PYTHON_SERVICE_URL}")
        print("  Run: docker-compose up --build")
        return False

    except Exception as e:
        print(f"✗ Health check failed: {str(e)}")
        return False


def create_test_pdf():
    """Create a simple test PDF using reportlab if available, or provide instructions"""
    print_section("2. Test PDF Preparation")

    # Check if a test PDF already exists
    test_pdf_path = Path("test_document.pdf")

    if test_pdf_path.exists():
        print(f"✓ Found existing test PDF: {test_pdf_path}")
        return test_pdf_path

    # Try to create one using reportlab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        print("Creating a test PDF...")

        c = canvas.Canvas(str(test_pdf_path), pagesize=letter)
        width, height = letter

        # Page 1
        c.setFont("Helvetica", 16)
        c.drawString(100, height - 100, "Test Document - Page 1")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 150, "This is a test PDF document for the RAG ingestion pipeline.")
        c.drawString(100, height - 180, "It contains multiple pages with sample text to test chunking.")
        c.drawString(100, height - 210, "The text should be extracted, chunked, and embedded properly.")

        # Add more content to create multiple chunks
        y_position = height - 250
        for i in range(10):
            text = f"This is sentence {i+1}. " * 10  # Long sentence to test chunking
            c.drawString(100, y_position, text[:80])
            y_position -= 20

        c.showPage()

        # Page 2
        c.setFont("Helvetica", 16)
        c.drawString(100, height - 100, "Test Document - Page 2")
        c.setFont("Helvetica", 12)
        c.drawString(100, height - 150, "This is the second page of the test document.")
        c.drawString(100, height - 180, "It should be processed separately and chunked appropriately.")

        y_position = height - 220
        for i in range(10):
            text = f"Page 2, sentence {i+1}. " * 8
            c.drawString(100, y_position, text[:80])
            y_position -= 20

        c.save()

        print(f"✓ Created test PDF: {test_pdf_path}")
        return test_pdf_path

    except ImportError:
        print("Note: reportlab not installed, cannot auto-generate test PDF")
        print("\nPlease create a test PDF manually or use an existing one:")
        print("  1. Create any PDF file and save it as 'test_document.pdf'")
        print("  2. Or specify a different PDF path in this script")
        print("\nInstall reportlab to auto-generate test PDFs:")
        print("  pip install reportlab")
        return None


def test_ingest_endpoint(pdf_path):
    """Test the /ingest endpoint with a PDF file"""
    print_section("3. Testing /ingest Endpoint")

    if not pdf_path or not pdf_path.exists():
        print("✗ No PDF file available for testing")
        return None

    try:
        print(f"Uploading PDF: {pdf_path}")
        print("This may take a minute for embedding generation...")

        with open(pdf_path, 'rb') as pdf_file:
            files = {'file': (pdf_path.name, pdf_file, 'application/pdf')}
            data = {'title': 'Phase 3 Test Document'}

            start_time = time.time()
            response = requests.post(INGEST_ENDPOINT, files=files, data=data, timeout=300)
            elapsed_time = time.time() - start_time

            response.raise_for_status()
            result = response.json()

            print(f"\n✓ Ingestion successful! (took {elapsed_time:.2f} seconds)")
            print(f"  Status: {result.get('status')}")
            print(f"  Document ID: {result.get('document_id')}")
            print(f"  Title: {result.get('title')}")
            print(f"  Number of chunks: {result.get('num_chunks')}")

            return result

    except requests.exceptions.Timeout:
        print("✗ Request timed out (this might happen for large PDFs)")
        print("  Check service logs: docker-compose logs -f python-service")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP error: {e}")
        if e.response is not None:
            print(f"  Response: {e.response.text}")
        return None

    except Exception as e:
        print(f"✗ Ingestion failed: {str(e)}")
        return None


def verify_database_records(document_id):
    """Verify that records were created in the database"""
    print_section("4. Verifying Database Records")

    if not document_id:
        print("✗ No document ID to verify")
        return False

    try:
        # Check documents table
        print("Checking documents table...")
        cmd = [
            "docker-compose", "exec", "-T", "db",
            "psql", "-U", "raguser", "-d", "ragdb",
            "-c", f"SELECT id, title, total_chunks, upload_timestamp FROM documents WHERE id = {document_id};"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Document record found:")
            print(result.stdout)
        else:
            print(f"✗ Error checking documents: {result.stderr}")
            return False

        # Check chunks table
        print("\nChecking chunks table...")
        cmd = [
            "docker-compose", "exec", "-T", "db",
            "psql", "-U", "raguser", "-d", "ragdb",
            "-c", f"SELECT COUNT(*), MIN(chunk_index), MAX(chunk_index) FROM chunks WHERE document_id = {document_id};"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Chunk records found:")
            print(result.stdout)
        else:
            print(f"✗ Error checking chunks: {result.stderr}")
            return False

        # Check embedding dimensions
        print("\nVerifying embedding dimensions...")
        cmd = [
            "docker-compose", "exec", "-T", "db",
            "psql", "-U", "raguser", "-d", "ragdb",
            "-c", f"SELECT array_length(embedding, 1) as dim, COUNT(*) FROM chunks WHERE document_id = {document_id} GROUP BY dim;"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Embedding dimensions:")
            print(result.stdout)
            if "384" in result.stdout:
                print("✓ Correct embedding dimension (384)")
            else:
                print("✗ Unexpected embedding dimension (expected 384)")
        else:
            print(f"✗ Error checking embeddings: {result.stderr}")
            return False

        # Sample some chunks
        print("\nSample chunk content (first 2 chunks)...")
        cmd = [
            "docker-compose", "exec", "-T", "db",
            "psql", "-U", "raguser", "-d", "ragdb",
            "-c", f"SELECT chunk_index, page_start, substring(content, 1, 100) as preview FROM chunks WHERE document_id = {document_id} ORDER BY chunk_index LIMIT 2;"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"✗ Error sampling chunks: {result.stderr}")

        return True

    except FileNotFoundError:
        print("✗ docker-compose not found")
        print("  Cannot verify database records without docker-compose")
        return False

    except Exception as e:
        print(f"✗ Verification failed: {str(e)}")
        return False


def check_service_logs():
    """Show recent service logs"""
    print_section("5. Service Logs (last 20 lines)")

    try:
        cmd = ["docker-compose", "logs", "--tail=20", "python-service"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"✗ Error getting logs: {result.stderr}")

    except FileNotFoundError:
        print("✗ docker-compose not found")

    except Exception as e:
        print(f"✗ Failed to get logs: {str(e)}")


def main():
    """Main test execution"""
    print("\n" + "=" * 70)
    print("  PHASE 3 INGESTION SERVICE TEST")
    print("=" * 70)

    # Step 1: Health check
    if not check_service_health():
        print("\n⚠ Please start the services first:")
        print("  docker-compose up --build")
        sys.exit(1)

    # Step 2: Prepare test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        print("\n⚠ Please provide a test PDF to continue")
        sys.exit(1)

    # Step 3: Test ingestion
    result = test_ingest_endpoint(pdf_path)
    if not result:
        print("\n⚠ Ingestion failed - check service logs")
        check_service_logs()
        sys.exit(1)

    # Step 4: Verify database
    document_id = result.get('document_id')
    if document_id:
        verify_database_records(document_id)

    # Step 5: Show logs
    check_service_logs()

    # Summary
    print_section("Test Summary")
    print("✓ All tests completed!")
    print(f"\nDocument ID {document_id} has been successfully ingested.")
    print("You can now:")
    print("  - Ingest more PDFs using the /ingest endpoint")
    print("  - Query chunks using vector similarity search")
    print("  - Implement the RAG query endpoint (Phase 4)")
    print("\nNext steps: See PHASE3_INGESTION.md for more details")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
