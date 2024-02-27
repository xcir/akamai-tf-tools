# modules.tf
# version 1.0.0
# This Terraform configuration functions as the configuration to create Akamai modules which acts as logical groupings of Akamai functionality.

module "akamai-property" {
    source = "./akamai-property"

    edgerc_config_section = var.edgerc_config_section

    contract_id = var.contract_id
    group_id    = var.group_id

    # 設定が必要なもの
    hostname        = "ホスト名を設定する"                          # akamaiで受け付けたいホスト名
    edge_hostname   = "エッジホスト名を設定する"                     # 既存でも新規でも
    origin_hostname = "オリジンホスト名"                            # example.netなど
    cpcode_name     = "CPコードの名前を設定"                        # 基本的にホスト名と同一
    default_ttl     = "デフォルトのTTL設定"                         # smhd(秒分時日) 30d=30日

    # 何かあれば変更するもの
    product_id      = "prd_Download_Delivery"   # prd_Download_Delivery, prd_Dynamic_Site_Del
    ip_behavior     = "IPV4"                    # IPV4(v4only) , IPV6_COMPLIANCE(v4/v6 dualstack)
    rule_format     = "latest"                  # latest, v2023-05-30

    cert_provisioning_type  = "CPS_MANAGED" 
}