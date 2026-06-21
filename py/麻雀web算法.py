import json,base64,hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def jsencode(data):
    """
    等效实现JS的jsencode函数
    :param data: 任意可JSON序列化的Python数据（字典/列表/字符串等）
    :return: 编码后的Base64字符串
    """
    # 1. 固定密钥（与JS一致）
    key = "Mcxos@mucho!nmme"
    key_len = len(key)

    # 2. 将输入数据序列化为JSON字符串（匹配JS的JSON.stringify行为）
    # ensure_ascii=False：避免Python默认转义非ASCII字符（JS不会转义）
    json_str = json.dumps(data, ensure_ascii=False)

    # 3. 第一次Base64编码（匹配JS的Base64.encode）
    # 先转UTF-8字节串 → Base64编码 → 转回字符串
    b64_1 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    # 4. 按位异或处理（核心逻辑）
    xor_result = []
    for i, char in enumerate(b64_1):
        # 密钥索引：循环取模密钥长度
        key_idx = i % key_len
        # 字符ASCII码异或
        xor_code = ord(char) ^ ord(key[key_idx])
        # 转回字符并保存
        xor_result.append(chr(xor_code))
    xor_str = "".join(xor_result)

    # 5. 第二次Base64编码并返回
    b64_2 = base64.b64encode(xor_str.encode("utf-8")).decode("utf-8")
    return b64_2


def decrypt(encrypted_str, viewport_meta_id, charset_meta_id):
    """
    JS decrypt函数的Python实现
    :param encrypted_str: 待解密的字符串（CryptoJS AES加密后的Base64字符串）
    :param viewport_meta_id: meta[name="viewport"]的id去掉"now_"后的字符串
    :param charset_meta_id: meta[charset="UTF-8"]的id去掉"now_"后的字符串
    :return: 解密后的明文
    """
    # 1. 构建id-text映射数组
    id_text_list = []
    for idx in range(len(charset_meta_id)):
        # 取charset_meta_id的字符作为id，viewport_meta_id对应位置作为text
        id_char = charset_meta_id[idx]
        text_char = viewport_meta_id[idx] if idx < len(viewport_meta_id) else ''
        id_text_list.append({
            "id": id_char,
            "text": text_char
        })

    # 2. 按id升序排序（id是字符型数字，需转int比较）
    id_text_list_sorted = sorted(id_text_list, key=lambda x: int(x["id"]))

    # 3. 拼接text得到密钥种子
    seed = ''.join([item["text"] for item in id_text_list_sorted])

    # 4. 计算MD5（拼接lemon后）
    md5_input = (seed + "lemon").encode("utf-8")
    md5_result = hashlib.md5(md5_input).hexdigest()  # 32位小写MD5字符串

    # 5. 提取AES密钥（后16位）和IV（前16位）
    aes_key = md5_result[16:].encode("utf-8")  # 16字节，符合AES-128要求
    aes_iv = md5_result[:16].encode("utf-8")  # 16字节IV

    # 6. AES-CBC解密（处理CryptoJS的Base64密文 + PKCS7解填充）
    # 步骤1：Base64解码密文（CryptoJS默认把密文存为Base64）
    cipher_data = base64.b64decode(encrypted_str)

    # 步骤2：创建AES解密器（CBC模式）
    cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)

    # 步骤3：解密并解填充（PKCS7）
    decrypted_data = cipher.decrypt(cipher_data)
    plain_data = unpad(decrypted_data, AES.block_size, style='pkcs7')

    # 步骤4：转UTF8字符串返回
    return plain_data.decode("utf-8")


# 测试示例
if __name__ == "__main__":
    print(jsencode('8345CKI5RmrTiUzkWYSidjsDMAnUo8ymRXmSJ5elQ6Ma'))
    print()
    print(decrypt('d/9dVloC8nw/2z9L79fLd4UGAXm6KAyQCgYJ26tFtwhlLVD7sYhE2LPrd31tkcct4XgvJc/MchhuOsIc7YLzbafajYrKhNVTIKyAk8Vrmcdh2oY8/xXDJCA+P8bfLrnvJQMGjFwLpwP1kkrIOQxioKAxf+xDFRLK/tElLRYSPHm9Yu/mKDnwi9SBSXfZCp4RuYgk7RfBAEra9sNcs2kMAbt2v23HPEMlPrdSCdmMA6DfbOIgrRerdfnvFuJd7ZC1J60oDRCw52OuRx2h6Cw3syk5SiO11lDTiSuYSluPwylj8Ee2Br0BOVgD1OaNQYVtMNd3qiwLpBv+s+1U/Yjfmkw0E2BlLnbBdPdkCebZYh0EV9+Yw3KFyvop6tIOkHjKnX/3DF46kt/GV8Rk+w2Fl6WZd0VHNEf9JkClGIDNdVwnMXhd4i4+coN2BItzAfRLKFl9LoRnqwgjDw5YKTyMM8RBuU28l5UIpmyJSh3oTBR1epURwoKC4eoGVWF47zSx05viiNix/ZySE0d8JTtgB83OHTaTvrWqL/VJR64Of0QPEti7DRkVzZG0pSi9b7j1LCdhugWTArIGBY5t0WrWHSLTUqEIFrvH+yPkCdsYf88=','QYqRNcZEyn','2630841957'))