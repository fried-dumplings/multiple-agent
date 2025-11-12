Pod::Spec.new do |s|
    s.name             = 'flutter_module'
    s.version          = '1.0.0'
    s.summary          = 'Flutter module'
    s.description      = 'Flutter compiled xcframeworks'
    s.homepage         = 'https://example.com'
    # s.license          = { :type => 'MIT', :file => 'LICENSE' }
    s.author           = { 'you' => 'you@example.com' }
    s.platform         = :ios, '13.0'
    s.source           = { :http => 'https://healthwhale-overseas-public-read.oss-ap-southeast-1.aliyuncs.com/MySDK1.zip' }
    # s.source           = { :http => 'https://healthwhale-overseas-public-read.oss-ap-southeast-1.aliyuncs.com/FlutterArtifacts-1.0.0.zip' }
    s.vendored_frameworks = '*.xcframework'

    s.dependency 'WebRTC-SDK'
    s.dependency 'Bugly'
   
  end
  