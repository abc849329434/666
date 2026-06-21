import base64, hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def aes_ecb_encrypt(plain_text, key='11GK2we32144LO&hilUITB)FMd1khdaF'):
    try:
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        padded_plain_bytes = pad(plain_text.encode('utf-8'), AES.block_size)
        cipher_bytes = cipher.encrypt(padded_plain_bytes)
        return base64.b64encode(cipher_bytes).decode('utf-8')
    except Exception as e:
        raise ValueError(f"加密失败：{str(e)}") from e

# 计算证书MD5/SHA1哈希
def cert_hash(base64_cert_str, pkg, ver):
    try:
        cert_binary = base64.b64decode(base64_cert_str)
        md5_upper = hashlib.md5(cert_binary).hexdigest().upper()
        sha1_upper = hashlib.sha1(cert_binary).hexdigest().upper()
        return f"{md5_upper}######{sha1_upper}~~~~~~{pkg}>>>+++{ver}"
    except Exception as e:
        print(f"处理过程中出现错误：{str(e)}")
        return None

def get_key(publickey, pkg, ver):
    concat_result = cert_hash(publickey, pkg, ver)
    print(concat_result)
    encrypted = aes_ecb_encrypt(concat_result)
    # print('加密结果：',encrypted)
    key_str = base64.b64encode(encrypted.encode('utf-8')).decode('utf-8')
    # print('key_str: ', key_str)
    return f'{key_str[:16]}{key_str[-16:]}'

if __name__ == "__main__":
    print('橘汁')
    version = 3017
    package = 'com.tjjiangh.android'
    cert_base64 = '''MIIDHjCCAgagAwIBAgIKWU0AAAAAAJ44DzANBgkqhkiG9w0BAQsFADAcMQswCQYDVQQGEwJDTjEN
    MAsGA1UEAwwEdGpqaDAgFw0yNTA1MjYxMTE4MDhaGA8yMDUwMDUyNzExMTgwOFowHDELMAkGA1UE
    BhMCQ04xDTALBgNVBAMMBHRqamgwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDVq3TE
    Hn+u+3M0YdWbmKfT7HIYjNEPdYIZfTwrtVB/QSPxdBQupYP209tqIhwwcvFlfKUyFVUk1r6P5FUL
    bxOxgcjHwJHdyc90Ev7Obc4rmTeS9uTPcE3dWgJwvAt8OUBPn09X1UmoGeW0GdNhOLfOYyHFgMuw
    zGLDB/YgSD7KjjCN0UhdZg7PqTlpLZDp6nxMqgMdcRoVMhhSw/Gp4LPSjL+GkUSWlIpxrVCG2V+Y
    j6Fnlx0QCOWyMzYivaEuWuAO3YZffT8zXwiCAM43jZ2X4AsVo9H7liqcB0PFsFQ6K4TI24E9cJOp
    In+7OSHw819FG5dHsyM8gWUS+8yvQtw7AgMBAAGjYDBeMAwGA1UdEwEB/wQCMAAwHwYDVR0jBBgw
    FoAUXlITfTYhEMHvKsN+kYKm1gstPwwwHQYDVR0OBBYEFF5SE302IRDB7yrDfpGCptYLLT8MMA4G
    A1UdDwEB/wQEAwIHgDANBgkqhkiG9w0BAQsFAAOCAQEAY+MorvbBjz1QKND/avHhreETJSTWWHtg
    t/3PUOc3XTerG3E04ruPqKBbE8XiaG3zp3kAOeN9Wo/LRqHQBJlivljtziPxTcpkzPHMFPjbq2Wt
    4c3YwFYpupJ+pJV4gsFFEa58beuDCLFUdBVcz4mZaw1QysX58WUodyvjH497QeBPZMV25U4nwhVy
    kNftyBvqUkf8iVXZDz7hJ1gbyaWWyDpzfuAEkp60hjU6Czz3i2/b0h6D2bb2w5UpClYBuTcgSn8t
    JZMSmhiaXpTeI+sDw1ElwGlsYzleVKmNQdiwmSDaPedSjPn11xJx61SOS8UFw3f2+41oFCvRUM/d
    wdpUBA==
    '''
    print('AesKey: ', get_key(cert_base64, package, version), '\n')

    print('电影天堂')
    version = 3006
    package = 'com.ddtaikzhilv.android'
    cert_base64 = '''MIIDIjCCAgqgAwIBAgIKWU0AAAAAAKLZ+TANBgkqhkiG9w0BAQsFADAeMQswCQYDVQQGEwJDTjEP
    MA0GA1UEAwwGZGR0a3psMCAXDTI1MDIxMTE1NDYyMFoYDzIwNTAwMjEyMTU0NjIwWjAeMQswCQYD
    VQQGEwJDTjEPMA0GA1UEAwwGZGR0a3psMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
    l/vzzRh6IT+mSa8IUhBDnqINeUo767jyJql+ETy7VnW/VfDKPT4bpEbsfGV6q9iDUxiaLiy/25XI
    35XiusDSAxTC/g0oZ/BG1BOcNxkgXBVMD5qDvMp8eFSzxc98Ms+wVZNLt+hFi8zz7+tS5uOifDm6
    PT6QQVqjwA20mH54UBGoeaLIzH1ykUEyXFA+u/NUxX4XNwC6OiH0DFGyc8MKbphxi5suMcCr7xUO
    4GzkjSe3TyWgX5GTXxUYGjchxqabPYKtO2BN8kIg1rbAMYWGmb2T5FPIFfE+83ObAKfRp/J04Ax0
    0WLrwcFMh5NdK42ctYjXJCcT6QRKR2KQZXgQdwIDAQABo2AwXjAMBgNVHRMBAf8EAjAAMB8GA1Ud
    IwQYMBaAFDZEX4Fi6/ceysr5K1jQGiQbtv0ZMB0GA1UdDgQWBBQ2RF+BYuv3HsrK+StY0BokG7b9
    GTAOBgNVHQ8BAf8EBAMCB4AwDQYJKoZIhvcNAQELBQADggEBAFOToEGeIeNNkuHdZJMzsCLfbiuM
    xgm3cNhptWzd1z0fAKLgJLEVTqQZwsm3kb+iOjvK7lFyXs0YCpzVNlNkir078LzRztWUPqaiF+en
    A6qLtWk4E40Ky9Mdh/4A1GQFwgSNGrHPaZTa9hPzKdsCjMYpUaTQ28aK/p28DyPj1gZQTWaZb/vE
    YQRFZ0V3gN1h6LZRBz3mR1mTDgExpx5/zp9TAVaQg0nhtTyoeyi85Co3IyWdMi2Kv6Vi8DKMmXry
    jikrar1sJ8AWaXy9F7sBNhfEDgqeET3O5tYzCSj6jChR7fP3kONYqnhABFd58/d3IZmIbSmGP2qf
    5ab/ifNk2bY=
    '''
    print('AesKey: ', get_key(cert_base64, package, version), '\n')

    print('小苹果')
    version = 1003
    package = 'com.juechufsh.android.xpg1'
    cert_base64 = '''MIIDIjCCAgqgAwIBAgIKWU0AAAAAAMmAnzANBgkqhkiG9w0BAQsFADAeMQswCQYDVQQGEwJDTjEP
    MA0GA1UEAwwGamNodWZzMCAXDTI1MDUyMDE1NDIyNFoYDzIwNTAwNTIxMTU0MjI0WjAeMQswCQYD
    VQQGEwJDTjEPMA0GA1UEAwwGamNodWZzMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
    iIMty8oxcewzTK1k69SStbt6h9ds5xzfObBMVE37PZe1iqd53Gx+pcmUQcO6c7N32ObE4gGAriXs
    SATnvtmFvfTsCAFiid0R4SqlJ8vqebI+Om3t3lGhlB1EThnWF1/gEjv+NIwuCTjsPpki4omEA7Nx
    tfQLhm/LbMEUhbhljER7v7Gz3G9JrCszZy105XL/T55LG2CEJOFMY1pxdHJnEddkuWX648Gsr1QZ
    oFRZgXEKy7jal32rsAozfEvixXoaZcP8AK/YM18LAlfYeiurbMV089fpyJF6J4edAqnYqui+TjIg
    SZ++Ztyu7uLfQtoHndNujmRGayQ8NN8zrljOuwIDAQABo2AwXjAMBgNVHRMBAf8EAjAAMB8GA1Ud
    IwQYMBaAFFbhjxtVW2PMDJYv5zRhTX9XboG3MB0GA1UdDgQWBBRW4Y8bVVtjzAyWL+c0YU1/V26B
    tzAOBgNVHQ8BAf8EBAMCB4AwDQYJKoZIhvcNAQELBQADggEBAFHTAbnL5O/KvVwb/zf9LIoYfDRp
    n/mvTkhFIxlZ9hKGlgvwHEbsiFSDJetoTAe+VgrGWsZzF08Y704b4/nLgaEk7d+PHq6JuuycUlXi
    2xlJruZJXoqUVGdGMc4sNKPV3iudzrd7mGB649i24/fiVdRIfqHrF4jyAVhYCKGKEfX/nkGjKM24
    Y+JkiVTC2iteCCalKQg0OGr7FuxAtjQdkk3OP4k+0aTpPZfhFll1kLsOuAcx0aLRTTO4iAwh1eG2
    waEHaiyUFUQo+03rb0a/y9u6wnq6F1aJDEk1eJ9vKl70mAlixvKLTnu4lRFo/qBSqDO0FfPd3GYU
    gJHMEmaEe34=
    '''
    print('AesKey: ', get_key(cert_base64, package, version), '\n')
