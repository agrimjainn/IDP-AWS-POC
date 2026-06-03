# 📄 Document Extractor - Intelligent Document Processing

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-Bedrock-orange?style=flat-square&logo=amazon)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

*Extract structured data from invoices and documents using advanced AI-powered processing engines*

</div>

---

## 🎯 Overview

**Document Extractor** is an intelligent document processing (IDP) application that automatically extracts structured data from PDF invoices and documents. It supports two powerful processing engines:

- **🚀 Amazon Bedrock** - Fast, synchronous processing using Claude's capabilities
- **⚡ AWS Bedrock Data Automation (BDA)** - Asynchronous batch processing for complex workflows

Perfect for automating invoice processing, data entry, and document digitization workflows.

---

## ✨ Features

- ✅ **Dual Processing Engines** - Choose between fast sync (Bedrock) or batch (BDA) processing
- 📋 **Automatic Data Extraction** - Extracts invoices headers, line items, and metadata
- 🎨 **Modern Web UI** - Beautiful, responsive interface with real-time feedback
- 📊 **Structured JSON Output** - Clean, standardized JSON format for easy integration
- 🔐 **Secure** - Environment-based configuration, no hardcoded secrets
- 🚀 **Production Ready** - Flask backend with CORS support
- 📥 **Batch Processing** - Process multiple documents efficiently

---

## 📊 Extracted Data Schema

### Header Fields
The application extracts the following header information from invoices:

| Field | Description | Example |
|-------|-------------|---------|
| **documentNumber** | Invoice/PO number | `INV-2024-001` |
| **purchaseOrderNumber** | PO reference | `PO-XYZ-123` |
| **documentDate** | Invoice date | `2024-03-15` |
| **dueDate** | Payment due date | `2024-04-15` |
| **senderName** | Vendor/Supplier name | `ABC Supplies Inc.` |
| **netAmount** | Subtotal before tax | `$1,000.00` |
| **taxAmount** | Tax/VAT amount | `$100.00` |
| **grossAmount** | Total amount due | `$1,100.00` |
| **shippingAmount** | Shipping cost | `$50.00` |
| **currencyCode** | Currency type | `USD` |
| **tariff** | Tariff/Classification | `HS-123456` |
| **freight** | Freight charges | `$25.00` |

### Line Items
For each line item in the invoice:

| Field | Description | Example |
|-------|-------------|---------|
| **description** | Item description | `Office Supplies` |
| **quantity** | Item quantity | `10` |
| **unitPrice** | Price per unit | `$50.00` |
| **netAmount** | Line item total | `$500.00` |
| **materialNumber** | SKU/Material ID | `MAT-001` |
| **unitOfMeasure** | Unit type | `BOX` |

---

## 🖥️ User Interface

### Modern Web Application

The application features a beautiful, responsive web interface built with:
- **Tailwind CSS** - Modern styling and responsive design
- **Lucide Icons** - Clean, professional iconography
- **Smooth Animations** - Blob animations and slide-in effects
- **Real-time Feedback** - Progress indicators and status updates

#### UI Sections:

1. **Mode Selection Screen**
   - Choose between Bedrock (Fast) or BDA (Batch) processing
   - Visual cards with descriptions of each option

2. **File Upload Area**
   - Drag-and-drop PDF upload
   - File validation and size limits (50MB max)
   - Visual success/error feedback

3. **Processing Animation**
   - Real-time progress indicators
   - Step-by-step status updates
   - Animated spinners and visual feedback

4. **Results Display**
   - Organized header fields in grid layout
   - Expandable line items section
   - Raw JSON output with syntax highlighting
   - Download JSON button for easy export

5. **Visual Features**
   - Gradient backgrounds with animated blobs
   - Pulsing glow effects on active selections
   - Smooth transitions and hover effects
   - Mobile-responsive layout

**To see the UI:** Open `document_processor_standalone.html` in a web browser

#### Screenshots

<div align="center">

**Mode Selection Screen**
![Mode Selection](./screenshots/01-mode-selection.png)
*Choose between Bedrock (fast sync) or BDA (batch processing)*

---

**File Upload Interface**
![File Upload](./screenshots/02-file-upload.png)
*Drag & drop PDF or click to browse. Supports up to 50MB*

---

**Processing Animation**
![Processing](./screenshots/03-processing.png)
*Real-time progress indicators show processing steps*

</div>

---

## 🛠️ Tech Stack

- **Backend:** Python 3.9+, Flask
- **Frontend:** HTML5, TailwindCSS, JavaScript
- **Cloud Services:** AWS S3, AWS Bedrock, AWS Bedrock Data Automation
- **Libraries:** boto3, flask-cors, werkzeug

---

## 📋 Requirements

- Python 3.9 or higher
- AWS Account with:
  - Bedrock API access
  - Bedrock Data Automation enabled
  - S3 buckets for input/output
- Valid AWS credentials (Access Key ID & Secret Access Key)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/document-extractor.git
cd document-extractor
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example configuration and add your AWS credentials:

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
# Add your AWS credentials, S3 buckets, ARNs, etc.
```

**Required Environment Variables:**
```dotenv
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
INPUT_BUCKET=my-idp-input-documents
OUTPUT_BUCKET=my-idp-extracted-data
BDA_PROJECT_ARN=arn:aws:bedrock:...
BDA_PROFILE_ARN=arn:aws:bedrock:...
```

### 5. Run the Backend

```bash
python backend_processor.py
```

The Flask server will start at `http://localhost:5000`

### 6. Open the UI

Open `document_processor_standalone.html` in your browser or serve it through a web server:

```bash
# Using Python
python -m http.server 8000

# Then open: http://localhost:8000/document_processor_standalone.html
```

---

## 📡 API Documentation

### Endpoint: `/api/process-documents`

**Method:** `POST`

**Parameters:**
- `files` (multipart/form-data) - PDF file(s) to process
- `mode` (string) - Processing engine: `bedrock` or `bda`

**Request Example:**
```bash
curl -X POST http://localhost:5000/api/process-documents \
  -F "files=@invoice.pdf" \
  -F "mode=bedrock"
```

**Response:**
```json
{
  "results": [
    {
      "success": true,
      "filename": "invoice.pdf",
      "extractedData": {
        "headerFields": {
          "documentNumber": "INV-001",
          "netAmount": "$1000",
          ...
        },
        "lineItemFields": [...]
      }
    }
  ]
}
```

### Endpoint: `/api/health`

**Method:** `GET`

Simple health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

## 🔄 Processing Workflows

### Bedrock Processing (Synchronous)
```
PDF Upload → Amazon Bedrock (Nova) → Extract Data → Return JSON
```
- ⚡ **Speed:** Immediate response (seconds)
- 📊 **Best For:** Single document processing
- 💰 **Cost:** Per invocation

### BDA Processing (Asynchronous)
```
PDF Upload → S3 → BDA Job Submit → Poll Status → S3 Fetch → Return JSON
```
- 🚀 **Speed:** Batch processing (minutes)
- 📦 **Best For:** Bulk document processing
- 💰 **Cost:** Fixed pricing

---

## 📦 Project Structure

```
document-extractor/
├── backend_processor.py          # Flask backend & processing logic
├── document_processor_standalone.html  # Web UI
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

---

## 🔐 Security

- ✅ No hardcoded secrets - all credentials in `.env`
- ✅ `.env` is git-ignored (won't be committed)
- ✅ `.env.example` provided as template
- ✅ CORS configured for trusted origins only
- ✅ File type validation (PDF only)
- ✅ File size limits (50MB max)

---

## 🚨 Troubleshooting

### ClientToken Validation Error
**Error:** `ValidationException: Member must satisfy regular expression pattern`

**Solution:** Ensure `clientToken` uses alphanumeric characters. The backend automatically generates valid tokens.

### AWS Credentials Not Found
**Error:** `Unable to locate credentials`

**Solution:** 
1. Create `.env` file from `.env.example`
2. Add your AWS credentials
3. Ensure credentials have Bedrock & S3 permissions

### S3 Bucket Access Denied
**Error:** `An error occurred (AccessDenied)`

**Solution:**
1. Verify bucket names in `.env`
2. Check IAM permissions for your AWS user
3. Ensure buckets exist in correct region

### Processing Timeout
**Error:** `BDA job ended with status: Failed`

**Solution:**
1. Check document format (must be valid PDF)
2. Verify BDA project ARN and profile ARN
3. Increase `BDA_TIMEOUT_SECONDS` in `.env`

---

## 📈 Performance

- **Bedrock:** 2-5 seconds per document
- **BDA:** 30-120 seconds per document (asynchronous)
- **Batch Capacity:** Limited by AWS API quotas
- **File Size:** Up to 50MB per document

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 💡 Tips & Best Practices

- **Use Bedrock** for quick, single-document processing
- **Use BDA** for batch processing of large document volumes
- **Keep `.env` secure** - never commit credentials to version control
- **Monitor AWS costs** - set up billing alerts for Bedrock/BDA usage
- **Test with sample invoices** first to verify extraction accuracy
- **Export results** as JSON for easy integration with other systems

---

## 🔗 Useful Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [AWS Bedrock Data Automation](https://docs.aws.amazon.com/bedrock/latest/userguide/data-automation.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

---

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

<div align="center">

Made with ❤️ for intelligent document processing

**[⬆ back to top](#-document-extractor---intelligent-document-processing)**

</div>
