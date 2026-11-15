$(call inherit-product, $(SRC_TARGET_DIR)/product/aosp_base.mk)
$(call inherit-product-if-exists, vendor/omni/config/common.mk)

PRODUCT_DEVICE := cannoli
PRODUCT_NAME := omni_cannoli
PRODUCT_BRAND := Amazon
PRODUCT_MANUFACTURER := Amazon
PRODUCT_MODEL := Echo Dot (5th Gen)
