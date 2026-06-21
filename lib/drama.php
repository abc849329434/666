<?php
header("Content-Type: text/json;charset=utf-8");
$name = $_GET['name']??die('name为空');

$timestamp = get13DigitTimestamp();
$random_str = randomStr();


if($name == 'dytt'){
$vApp = '3001';  // versionCode
$vName = '3.0.0.1';  // versionName
$appName = '电影天堂';   // 应用名称
$pkg = 'com.ddtaikzhilv.android';  // 应用包名
$publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCduNEnfxGaLuQRk5ABzXHhPV43zi00sCHjLo8BYc+Wi6xXm2b4v0i28Sq4WlNCKhseft9fz8kO/qLr6/022o1RcuOU7e4GFL3U9WnNODwRBYSYWd+K8nqpI/tAUDmZEBGRWqjrc7x6aMl3A+xpnWkLbPCLsuhbuuUE3tv09oeOpwIDAQAB';}
elseif($name == 'juzhi'){
$vApp = '3014';  // versionCode
$vName = '3.0.1.4';  // versionName
$appName = '橘汁';   // 应用名称
$pkg = 'com.xczmorisc.android';  // 应用包名
$publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCp9Ek4wIlQAtwFnuBRlsFiow2tr+4UOciGeNKbY7nL74etUqUb6fvpOSOHhFEfaWlfwUpOB17x3JEL3No19nfjCeVYrYPjlJcgoqUWH/tfIfFAQWvtxBIBlKazkhw8d3ChysWmeWRikKqkBsVRY4oqNPuj4sjm6Zult0U4I4prRQIDAQAB';}
elseif($name == 'jujiwu'){
$vApp = '3002';  // versionCode
$vName = '3.0.0.2';  // versionName
$appName = '剧集屋';   // 应用名称
$pkg = 'com.dandanaixc.android';  // 应用包名
$publicKey = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCduNEnfxGaLuQRk5ABzXHhPV43zi00sCHjLo8BYc+Wi6xXm2b4v0i28Sq4WlNCKhseft9fz8kO/qLr6/022o1RcuOU7e4GFL3U9WnNODwRBYSYWd+K8nqpI/tAUDmZEBGRWqjrc7x6aMl3A+xpnWkLbPCLsuhbuuUE3tv09oeOpwIDAQAB';}
else{
die('请按要求传参');
}

$androidID = '313c3eeeb2a098a1';
$mac = '02:00:00:00:00:00';   // 网卡MAC地址
$model = '23113RKC6C';  // 型号
$facturer = 'Xiaomi';  // 制造商

$uuid = strtoupper(md5($androidID.$mac.$model.$facturer));
$sign = openssl_encrypt($timestamp.$random_str,'AES-256-ECB','OC1A06E197EF10CF3F6058CA7A803B5E',0);

$deviceInfo = [
    "country" => "CN",
    "vName" => $vName,
    "cpuId" => "",
    "young" => 0,
    "facturer" => $facturer,
    "pkg" => $pkg,
    "uuid" => $uuid,
    "resolution" => "900x1600",
    "mac" => urlencode($mac),
    "sig" => rsaEncrypt($timestamp.$random_str.$vApp),
    "abid" => "6249",
    "model" => $model,
    "plat" => "android",
    "udid" => $uuid,
    "dpi" => "240",
    "net" => "1",
    "lang" => "zh",
    "random_str" => $random_str,
    "brand" => "Redmi",  // 品牌
    "timestamp" => $timestamp,
    "density" => "3.25",
    "appName" => urlencode($appName),
    "cpu" => "arm64-v8a",
    "chid" => "10000",
    "carrier" =>  urlencode('移动') ,  // 网络运营商
    "sig2" => substr($sign,0,8),
    "sig3" => substr($sign,8),
    "_vOsCode" => "32",
    "vOs" => "12",  // 安卓版本
    "vApp" => $vApp,
    "device" => "0",
    "androidID" => $androidID
];

$dat = json_encode($deviceInfo);

$dat2 = openssl_encrypt($dat,'AES-128-CBC','ed5fdsgucxumegqa',1,'ed5fdsgucxumegqa');
$dat3 = bin2hex($dat2);
die($dat3);


function rsaEncrypt($plaintext) {
    global $publicKey;
    $publicKey = "-----BEGIN PUBLIC KEY-----\n" . wordwrap($publicKey, 64, "\n", 1) . "\n-----END PUBLIC KEY-----";
    $keyResource = openssl_pkey_get_public($publicKey);
    
    if (!$keyResource) {
        throw new Exception('公钥无效: ' . openssl_error_string());
    }
    $encrypted = '';
    $success = openssl_public_encrypt($plaintext, $encrypted, $keyResource, OPENSSL_PKCS1_PADDING);
    openssl_free_key($keyResource);
    
    if (!$success) {
        throw new Exception('加密失败: ' . openssl_error_string());
    }
    return base64_encode($encrypted);
}

function randomStr($i = 16) {
    $charArray = str_split("1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz");
    $str = '';
    $i2 = 0;
    
    while ($i2 < $i - 1) {
        $randomIndex = rand(0, 61);
        $c = $charArray[$randomIndex];
        
        if (strpos($str, $c) !== false) {
            $i2--;
        } else {
            $str .= $c;
        }
        $i2++;
    }
    
    return $str . "=";
}

function get13DigitTimestamp() {
    $microtime = microtime(true);
    $timestamp = (int)round($microtime * 1000);
    return $timestamp;
}