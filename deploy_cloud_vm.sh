#!/bin/bash
# ============================================
# ☁️ PLATINUM TIER - DEPLOY CLOUD VM
# Oracle Cloud Free Tier Setup
# ============================================
# Run this script on your local machine to prepare Oracle Cloud VM
# Then SSH into VM and run deploy_cloud_agent.sh

set -e

echo "============================================"
echo "☁️  PLATINUM TIER - CLOUD VM DEPLOYMENT"
echo "============================================"

# Configuration
VM_NAME="ai-employee-cloud"
COMPARTMENT_ID="ocid1.compartment.oc1..xxxxxx"  # Replace with your compartment ID
IMAGE_ID="ocid1.image.oc1..xxxxxx"  # Ubuntu 22.04
SHAPE="VM.Standard.A1.Flex"
OCPUS="2"
MEMORY="12"
BOOT_VOLUME="200"

echo ""
echo "Step 1: Create VM Instance"
echo "----------------------------------------"

# Create VM using OCI CLI
oci compute instance launch \
    --compartment-id $COMPARTMENT_ID \
    --display-name $VM_NAME \
    --shape $SHAPE \
    --shape-config '{"ocpus":'$OCPUS',"memoryInGBs":'$MEMORY'}' \
    --image-id $IMAGE_ID \
    --boot-volume-size-in-gbs $BOOT_VOLUME \
    --assign-public-ip true \
    --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \
    --wait

echo "✅ VM instance created!"

echo ""
echo "Step 2: Configure Security List"
echo "----------------------------------------"

# Allow SSH (port 22), HTTPS (443), Odoo (8069)
echo "⚠️  Please configure security list in Oracle Cloud Console:"
echo "   - Ingress Rules: Allow ports 22, 443, 8069"
echo "   - Or run: oci network security-list create ..."

echo ""
echo "Step 3: Get Public IP"
echo "----------------------------------------"

# Get VM public IP
PUBLIC_IP=$(oci compute instance get --instance-id <INSTANCE_ID> --query 'data."public-ip"' --raw-output)
echo "Public IP: $PUBLIC_IP"

echo ""
echo "Step 4: SSH into VM"
echo "----------------------------------------"
echo "Run: ssh -i ~/.ssh/id_rsa ubuntu@$PUBLIC_IP"

echo ""
echo "Step 5: Deploy Cloud Agent on VM"
echo "----------------------------------------"
echo "After SSH, run: ./deploy_cloud_agent.sh"

echo ""
echo "============================================"
echo "✅ CLOUD VM DEPLOYMENT COMPLETE"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Configure security list (ports 22, 443, 8069)"
echo "2. SSH into VM: ssh ubuntu@<public-ip>"
echo "3. Run deploy_cloud_agent.sh on VM"
echo "4. Setup Git sync"
echo "5. Start Cloud Agent with PM2"
echo ""
