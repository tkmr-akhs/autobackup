# モジュール, クラス, 関数


|module   |class etc.                |member                      |type            |description
|:--------|:-------------------------|:---------------------------|:---------------|:-
|main     |Main                      |execute                     |instance method |プログラムのエントリー ポイント。
|cnf      |CNF_DIR                   |-                           |constant        |設定ファイルがあるディレクトリ パスの既定値。
|^        |DEFAULT_CNF               |-                           |constant        |既定の設定を定義したファイルの名前の既定値。
|^        |USR_CNF                   |-                           |constant        |ユーザーが定義する設定を記したファイルの名前の既定値。
|^        |LOG_CNF                   |-                           |constant        |ログ設定ファイルの既定の名前。
|^        |CnfError                  |-                           |exception       |アプリ設定の整合性チェックに失敗したときに発生する例外。
|^        |ConfigurationLoader       |get_app_cnf                 |instance method |アプリ設定を取得します。アプリ設定は既定設定, ユーザー設定, コマンドライン オプション設定をマージしたものです。
|^        |^                         |get_log_cnf                 |instance method |ログ設定ファイルを取得します。
|^        |get_cli_cnf               |-                           |function        |コマンドライン引数をパースして、コマンドライン オプション設定を得ます。
|^        |merge_app_cnf             |-                           |function        |既定設定に、ユーザー設定, コマンドライン オプション設定をマージして、最終的にアプリに適用する設定にします。
|^        |validate_app_cnf          |-                           |function        |アプリ設定の整合性をチェックします。
|appinit  |init_app                  |-                           |function        |アプリの初期化を実施します。(一時ファイル置き場となるディレクトリの作成など)
|repoinit |BackupRepositoryFactory   |get_source_repository       |instance method |SourceRepository のインスタンスを得ます。
|^        |^                         |get_destination_repository  |instance method |DestinationRepository のインスタンスを得ます。
|^        |^                         |get_all_file_scanner        |instance method |AllFileScanner のインスタンスを得ます。
|^        |MetadataRepositoryFactory |get_metadata_repository     |instance method |MetadataRepository のインスタンスを得ます。
|bkup     |BackupFacade              |execute                     |instance method |引数として得た各リポジトリを使用して、一連のバックアップ処理を行います。
|srcrepo  |SourceRepository          |get_all_files               |instance method |バックアップの対象ファイルとなりうるすべてのファイル情報を取得します。 (バックアップが保存されたディレクトリを無視することにより、概念的にディスティネーションとは分割されたリポジトリとして扱えるようにします)
|^        |^                         |get_files_matching_criteria |instance method |条件に合致した対象ファイル情報を取得します。
|dstrepo  |DestinationRepository     |get_all_backups             |instance method |すべてのバックアップ先ファイル情報を取得します。 (バックアップ ファイル パスの正規表現に合致するファイルのみを抽出することにより、概念的にソースとは分割されたリポジトリとして扱えるようにします)
|^        |^                         |get_dst_file                |instance method |バックアップ対象ファイル情報を渡し、バックアップ ファイルのパスを得ます。
|^        |^                         |create_backup               |instance method |バックアップ対象ファイル情報を渡し、そのファイルをバックアップします。
|^        |^                         |create_backups              |instance method |バックアップ対象ファイル情報のリストを渡し、一括でそれらのファイルをバックアップします。
|^        |^                         |get_discard_list            |instance method |破棄予定の古いバックアップのリストを得ます。
|^        |^                         |remove_backup               |instance method |バックアップを削除します。
|^        |^                         |remove_backups              |instance method |削除するバックアップのリストを渡し、一括で削除します。
|metarepo |Metadata                  |key                         |instance field  |データベースのキーです。ノーマライズした絶対パスが利用されます。
|^        |^                         |mtime                       |instance field  |対象ファイルの更新日時です。
|^        |MetadataRepository        |get_metadata                |instance method |キーを指定してメタデータを取得します。
|^        |^                         |get_all_metadatas           |instance method |すべてのメタデータを取得します。
|^        |^                         |get_uncontained_key         |instance method |キーのリストを渡し、渡されたリストには含まれず、リポジトリ内にのみ含まれるキーを返します。(渡されたリストにだけあるキーや、両方に含まれるキーは無視されます。)
|^        |^                         |remove_metadata             |instance method |メタデータを削除します。
|^        |^                         |remove_metadatas            |instance method |削除するメタデータのリストを渡し、一括で削除します。
|^        |^                         |update_metadata             |instance method |メタデータを更新します。現在含まれていないキーのメタデータは、新規登録されます。
|scanner  |AllFileScanner            |get_all_files               |instance method |アプリ設定により指定された複数ディレクトリをスキャンし、配下にあるすべてのファイル情報を取得します。
|fsutil   |ScanLoopError             |-                           |exeption        |recursive_scandir でシンポリックリンクを辿り、ループを検出した際に発生する例外。
|^        |RecursiveScanDir          |recursive_scandir           |instance method |ディレクトリを指定し、配下のファイルをスキャンします。
|^        |FoundFile                 |path                        |instance field  |recursive_scandir で見つかったファイルを示す pathlib.Path オブジェクト。
|^        |^                         |scan_root_path              |instance field  |recursive_scandir を開始したディレクトリを示す pathlib.Path オブジェクト。
|^        |^                         |relpath                     |property        |path を示す、scan_root_path からの相対パス
|^        |^                         |normpath_str                |property        |path のノーマライズされた絶対パス。
|^        |^                         |mtime                       |property        |path の最終更新日時。
|^        |^                         |name                        |property        |path のファイル名。
|^        |^                         |stem                        |property        |path のファイル名の拡張子以外の部分。
|^        |^                         |suffix                      |property        |path のファイル名の拡張子。
|^        |^                         |parent                      |property        |path があるディレクトリを示す pathlib.Path オブジェクト。
|^        |^                         |samefile                    |instance method |path と、引数のパスが同じファイルを示すか。
|^        |^                         |is_symlink                  |instance method |path がシンボリック リンクか。
|^        |^                         |exists                      |instance method |path が示すファイルが存在するか。
|^        |^                         |is_hidden                   |instance method |path が示すファイルが隠しファイルか。
|dictutil |recursive_merge           |-                           |function        |dict を再帰的にマージします。

- SourceRepository, DestinationRepositry, AllFileScanner は互いに整合した動作が必要であるため、ファクトリからオブジェクトを得るようにしています。
- main.Main のイニシャライザーでは、コンフィグの生成とロギング設定までを、main.Main.execute では BackupFacade へのコンフィグの適用を、bkup.BackupFacade では実際のバックアップ処理を、それぞれ行うように切り分けています。
- main モジュールのテストは、ユニット テストは準備せず、インテグレーション テストとして位置づけています。