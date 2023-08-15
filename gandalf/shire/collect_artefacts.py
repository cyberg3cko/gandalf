#!/usr/bin/env python3 -tt
import hashlib
import os
import shutil
import subprocess
from datetime import datetime
from zipfile import ZipFile


def audit_log(gandalf_host, artefact):
    now_time = "{}Z".format(str(datetime.now()).replace(" ", "T"))
    with open(os.path.join(gandalf_host, "log.audit"), "a") as gandalf_audit:
        gandalf_audit.write(
            "{}Z,{},{},collected\n".format(
                now_time, gandalf_host.split("/")[-1], artefact
            )
        )


def audit_meta(gandalf_host, artefact):
    sha256 = hashlib.sha256()
    with open(artefact, "rb") as metafile:
        buffer = metafile.read(262144)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = metafile.read(262144)
    artefact_hash = sha256.hexdigest()
    with open(os.path.join(gandalf_host, "log.meta"), "a") as gandalf_meta:
        gandalf_meta.write(
            "{},{},{}\n".format(gandalf_host.split("/")[-1], artefact, artefact_hash)
        )


def make_artefact_dir(gandalf_artefact_destination, artefact_output_dir):
    if not os.path.exists(
        os.path.join(gandalf_artefact_destination, artefact_output_dir)
    ):
        os.makedirs(os.path.join(gandalf_artefact_destination, artefact_output_dir))
    else:
        pass


def copy_file(source, destination):
    if os.stat(source).st_size > 0:
        try:
            shutil.copy2(source, destination)
        except PermissionError:
            pass
        except FileExistsError:
            pass
    else:
        pass


def copy_dir(source, destination):
    if os.path.exists(source) and len(os.listdir(source)) != 0:
        try:
            shutil.copytree(source, destination)
        except PermissionError:
            pass
        except FileExistsError:
            pass
        except shutil.Error:
            pass
    else:
        pass


def print_progress(artefact, gandalf_host, artefact_output_dir, previously_collected):
    if os.path.exists(artefact):
        if (
            artefact_output_dir == "logs"
            or artefact_output_dir == "plists"
            or artefact_output_dir == "services"
        ):
            if artefact_output_dir == "logs":
                print(
                    "      \033[1;32mAcquired {} {} from '{}'\033[1;m".format(
                        artefact.split("/")[-3].lower(), artefact_output_dir, gandalf_host
                    )
                )
            elif artefact_output_dir == "plists":
                if len(artefact.split("/")) == 5:
                    print(
                        "      \033[1;32mAcquired {} {} {} from '{}'\033[1;m".format(
                            artefact.split("/")[-4].lower(),
                            artefact.split("/")[-2].lower(),
                            artefact_output_dir,
                            gandalf_host,
                        )
                    )
                elif len(artefact.split("/")) == 4:
                    print(
                        "      \033[1;32mAcquired {} {} {} from '{}'\033[1;m".format(
                            artefact.split("/")[-3].lower(),
                            artefact.split("/")[-2].lower(),
                            artefact_output_dir,
                            gandalf_host,
                        )
                    )
                else:
                    pass
            else:
                print(
                    "      \033[1;32mAcquired {} from '{}'\033[1;m".format(
                        artefact_output_dir, gandalf_host
                    )
                )
        elif artefact_output_dir == "memory":
            if artefact_output_dir not in str(previously_collected):
                print(
                    "      \033[1;32mAcquired {} artefacts from '{}'\033[1;m".format(
                        artefact_output_dir, gandalf_host
                    )
                )
            else:
                pass
            previously_collected.append("memory")
        elif artefact_output_dir == "cron":
            if artefact_output_dir not in str(previously_collected):
                print(
                    "      \033[1;32mAcquired {} artefacts from '{}'\033[1;m".format(
                        artefact_output_dir, gandalf_host
                    )
                )
            else:
                pass
            previously_collected.append("cron")
        elif artefact_output_dir == "conf":
            print(
                "      \033[1;32mAcquired configuration files from '{}'\033[1;m".format(
                    gandalf_host
                )
            )
        elif artefact_output_dir != "":
            print(
                "      \033[1;32mAcquired {} artefacts from '{}'\033[1;m".format(
                    artefact_output_dir, gandalf_host
                )
            )
        else:
            pass
    else:
        pass
    return previously_collected


def collect_volatile_data(gandalf_artefact_destination):
    platform = str(
        subprocess.Popen(
            ["uname", "-a"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()[0]
    )[2:-3]
    with open(os.path.join(gandalf_artefact_destination, "host.info"), "w") as platform_info:
        platform_info.write(platform)
    processes = str(
        subprocess.Popen(
            ["ps", "aux"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).communicate()[0]
    )[2:-3]
    with open(os.path.join(gandalf_artefact_destination, "process.info"), "w") as process_info:
        process_info.write(processes)
    try:
        netstat = str(
            subprocess.Popen(
                ["netstat"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()[0]
        )[2:-3]
        with open(os.path.join(gandalf_artefact_destination, "netstat.info"), "w") as netstat_info:
            netstat_info.write(netstat)
    except:
        pass
    try:
        ss = str(
            subprocess.Popen(
                ["ss"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).communicate()[0]
        )[2:-3]
        with open(os.path.join(gandalf_artefact_destination, "ss.info"), "w") as ss_info:
            ss_info.write(ss)
    except:
        pass
    print("      \033[1;32mAcquired volatile data from '{}'\033[1;m".format(gandalf_artefact_destination.split("/")[-2]))


def collect_browser_artefact(
    artefact_source, gandalf_artefact_destination, user_profile, browser, browser_file
):
    if not os.path.exists(
        os.path.join(
            gandalf_artefact_destination,
            "browsers",
        )
    ):
        os.mkdir(
            os.path.join(
                gandalf_artefact_destination,
                "browsers",
            )
        )
    else:
        pass
    if not os.path.exists(
        os.path.join(
            gandalf_artefact_destination,
            "browsers",
            browser,
        )
    ):
        os.mkdir(
            os.path.join(
                gandalf_artefact_destination,
                "browsers",
                browser,
            )
        )
    else:
        pass
    shutil.copy2(
        artefact_source,
        os.path.join(
            gandalf_artefact_destination,
            "browsers",
            browser,
            "{}+{}".format(
                user_profile,
                browser_file,
            ),
        ),
    )


def archive_artefacts(encryption, gandalf_destination, gandalf_host):
    gandalf_archive = os.path.join(
        gandalf_destination, "{}.zip".format(gandalf_host.split("/")[-1])
    )
    cwd = os.getcwd()
    os.chdir(os.path.join(gandalf_host, ".."))
    with ZipFile(gandalf_archive, "w") as gandalf_archive:
        if encryption.title() == "Key":
            pyminizip.compress(
                gandalf_host,
                gandalf_destination,
                gandalf_archive.split("/")[-1],
                "password",
                5,
            )
            """status = gpg.encrypt_file(gandalf_archive, ["gandalf@middle.earth"], output = gandalf_archive + ".enc")
            #with ZipFile(gandalf_archive, "r") as gandalf_archive:
                #status = gpg.encrypt_file(gandalf_archive, ["gandalf@middle.earth"], output = gandalf_archive + ".enc")
                #status = gpg.encrypt_file(gandalf_archive, encryption_object, output = gandalf_archive + ".enc")
            print(status.ok)
            print(status.stderr)"""
        elif encryption.title() == "Password":
            gandalf_archive.setpassword(bytes(encryption))
        else:
            pass
        for archiveroot, archivedirs, archivefiles in os.walk(
            gandalf_host.split("/")[-1]
        ):
            try:
                for archivefile in archivefiles:
                    gandalf_archive.write(os.path.join(archiveroot, archivefile))
            except ValueError as error:
                if "ZIP does not support timestamps before 1980" in str(error):
                    print("       \033[1;31mWARNING: '{}' could not be archived for '{}' as the timestamp is before 1980\033[1;m".format(os.path.join(archiveroot.split("/artefacts")[1], archivefile), gandalf_host.split("/")[-1]))
                else:
                    print("       \033[1;33mERROR: {}\033[1;m".format(error))
            try:
                for archivedir in archivedirs:
                    gandalf_archive.write(os.path.join(archiveroot, archivedir))
            except ValueError as error:
                if "ZIP does not support timestamps before 1980" in str(error):
                    print("       \033[1;31mWARNING: '{}' could not be archived for '{}' as the timestamp is before 1980\033[1;m".format(os.path.join(archiveroot.split("/artefacts")[1], archivedir), gandalf_host.split("/")[-1]))
                else:
                    print("       \033[1;33mERROR: {}\033[1;m".format(error))
    os.chdir(cwd)


def acquire_artefacts(
    encryption,
    system_artefacts,
    acquisition,
    # output_directory,
    # memory,
    # show_progress,
    # collect_files,
    # no_prompt,
    # encryption_object,
    # gpg,
    # pyminizip,
    gandalf_destination,
    gandalf_host,
):
    previously_collected = []
    os.mkdir(gandalf_host)
    with open(os.path.join(gandalf_host, "log.audit"), "a") as gandalf_audit:
        gandalf_audit.write("datetime,hostname,artefact,collected\n")
    gandalf_artefact_destination = os.path.join(gandalf_host, "artefacts")
    os.mkdir(gandalf_artefact_destination)
    collect_volatile_data(gandalf_artefact_destination)
    """if filelisting:
        with open(
            os.path.join(gandalf_artefact_destination, "file_directory_listing.csv"), "w"
        ) as file_listing:
            file_listing.write("path,file\n")
    else:
        pass
    for gandalfroot, _, gandalffiles in os.walk("/"):
        for gandalffile in gandalffiles:
            with open(
                os.path.join(
                    gandalf_artefact_destination, "file_directory_listing.csv"
                ),
                "a",
            ) as file_listing:
                file_listing.write("{},{}\n".format(gandalfroot, gandalffile))"""
    for artefact, artefact_output_dir in system_artefacts.items():
        if os.path.exists(artefact):
            if not artefact.endswith("/") and artefact_output_dir == "":  # file
                copy_file(artefact, gandalf_artefact_destination)
            else:  # directory
                if artefact_output_dir == "memory":
                    make_artefact_dir(gandalf_artefact_destination, artefact_output_dir)
                    if artefact.split("/")[-2] == "vm":
                        copy_file(
                            artefact,
                            os.path.join(
                                gandalf_artefact_destination,
                                artefact_output_dir,
                                "{}+{}".format(
                                    artefact.split("/")[-2], artefact.split("/")[-1]
                                ),
                            ),
                        )
                    else:
                        copy_file(
                            artefact,
                            os.path.join(
                                gandalf_artefact_destination,
                                artefact_output_dir,
                                artefact.split("/")[-1],
                            ),
                        )
                else:
                    pass
                for gandalfroot, gandalfdirs, gandalffiles in os.walk(artefact):
                    if (
                        artefact_output_dir == "boot"
                        or artefact_output_dir == "home"
                        or artefact_output_dir == "root"
                    ):
                        if not os.path.exists(
                            os.path.join(
                                gandalf_artefact_destination, gandalfroot.split("/")[1]
                            )
                        ):
                            copy_dir(
                                "/{}".format(gandalfroot.split("/")[1]),
                                os.path.join(
                                    gandalf_artefact_destination,
                                    gandalfroot.split("/")[1],
                                ),
                            )
                        else:
                            pass
                    else:
                        pass
                    if artefact_output_dir == "cron":
                        make_artefact_dir(
                            gandalf_artefact_destination, artefact_output_dir
                        )
                        for cronobject in os.listdir(artefact):
                            if os.path.isfile(os.path.join(artefact, cronobject)):
                                copy_file(
                                    os.path.join(artefact, cronobject),
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        "{}+{}".format(
                                            artefact.split("/")[-2], cronobject
                                        ),
                                    ),
                                )
                            elif os.path.isdir(os.path.join(artefact, cronobject)):
                                copy_dir(
                                    os.path.join(artefact, cronobject),
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        "{}+{}".format(
                                            artefact.split("/")[-2], cronobject
                                        ),
                                    ),
                                )
                            else:
                                pass
                    else:
                        pass
                    if artefact_output_dir == "tmp":
                        make_artefact_dir(
                            gandalf_artefact_destination, artefact_output_dir
                        )
                        for tmpobject in os.listdir(artefact):
                            if os.path.isfile(os.path.join(artefact, tmpobject)):
                                copy_file(
                                    os.path.join(artefact, tmpobject),
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        tmpobject,
                                    ),
                                )
                            elif (
                                os.path.isdir(os.path.join(artefact, tmpobject))
                                and "gandalf" != tmpobject
                            ):
                                copy_dir(
                                    os.path.join(artefact, tmpobject),
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        tmpobject,
                                    ),
                                )
                            else:
                                pass
                    else:
                        pass
                    if artefact_output_dir == "logs":
                        make_artefact_dir(
                            gandalf_artefact_destination, artefact_output_dir
                        )
                        for gandalffile in gandalffiles:
                            if gandalffile.endswith(".log"):
                                artefact_path = os.path.join(gandalfroot, gandalffile)
                                copy_file(
                                    artefact_path,
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        "{}+{}".format(
                                            artefact_path.split("/")[-2],
                                            artefact_path.split("/")[-1],
                                        ),
                                    ),
                                )
                            else:
                                pass
                    else:
                        pass
                    if artefact_output_dir == "plists":
                        make_artefact_dir(
                            gandalf_artefact_destination, artefact_output_dir
                        )
                        for gandalffile in gandalffiles:
                            if gandalffile.endswith(".plist"):
                                artefact_path = os.path.join(gandalfroot, gandalffile)
                                copy_file(
                                    artefact_path,
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        "{}+{}".format(
                                            artefact_path.split("/")[-2],
                                            artefact_path.split("/")[-1],
                                        ),
                                    ),
                                )
                            else:
                                pass
                    else:
                        pass
                    if artefact_output_dir == "services":
                        make_artefact_dir(
                            gandalf_artefact_destination, artefact_output_dir
                        )
                        for gandalffile in gandalffiles:
                            if (
                                gandalffile.endswith(".service")
                                or gandalffile.endswith(".socket")
                                or gandalffile.endswith(".target")
                            ):
                                artefact_path = os.path.join(gandalfroot, gandalffile)
                                copy_file(
                                    artefact_path,
                                    os.path.join(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                        "{}+{}".format(
                                            artefact_path.split("/")[-2],
                                            artefact_path.split("/")[-1],
                                        ),
                                    ),
                                )
                            else:
                                pass
                    else:
                        pass
                    if artefact_output_dir == "user":
                        if gandalfroot == "/Users/":
                            for user_profile in gandalfdirs:
                                usergandalfroot = os.path.join(
                                    gandalfroot, user_profile
                                )
                                for userobject in os.listdir(usergandalfroot):
                                    make_artefact_dir(
                                        gandalf_artefact_destination,
                                        artefact_output_dir,
                                    )
                                    if (
                                        os.path.exists(
                                            os.path.join(
                                                usergandalfroot, ".bash_history"
                                            )
                                        )
                                        or os.path.exists(
                                            os.path.join(usergandalfroot, ".bashrc")
                                        )
                                        or os.path.exists(
                                            os.path.join(usergandalfroot, ".local")
                                        )
                                        or os.path.exists(
                                            os.path.join(usergandalfroot, "Desktop")
                                        )
                                        or os.path.exists(
                                            os.path.join(usergandalfroot, "Public")
                                        )
                                    ):
                                        make_artefact_dir(
                                            os.path.join(
                                                gandalf_artefact_destination,
                                                artefact_output_dir,
                                            ),
                                            user_profile,
                                        )
                                    else:
                                        pass
                                    if os.path.isfile(
                                        os.path.join(usergandalfroot, userobject)
                                    ):
                                        if (
                                            userobject == ".bash_aliases"
                                            or userobject == ".bash_history"
                                            or userobject == ".bash_logout"
                                            or userobject == ".bashrc"
                                            or userobject == ".bash_profile"
                                            or userobject == ".bash_session"
                                        ):
                                            copy_file(
                                                os.path.join(
                                                    usergandalfroot, userobject
                                                ),
                                                os.path.join(
                                                    gandalf_artefact_destination,
                                                    artefact_output_dir,
                                                    user_profile,
                                                    userobject,
                                                ),
                                            )
                                        else:
                                            pass
                                    else:
                                        if (
                                            userobject == ".ssh"
                                            or userobject == ".Trash"
                                        ):
                                            copy_dir(
                                                os.path.join(
                                                    gandalfroot,
                                                    user_profile,
                                                    userobject,
                                                ),
                                                os.path.join(
                                                    gandalf_artefact_destination,
                                                    "user",
                                                    user_profile,
                                                    userobject.replace(".", ""),
                                                ),
                                            )
                                        elif userobject == "Library":
                                            userlibraryroot = os.path.join(
                                                gandalfroot, user_profile, userobject
                                            )
                                            for librarysubdir in os.listdir(
                                                userlibraryroot
                                            ):
                                                if librarysubdir == "Keychains":
                                                    if os.path.exists(
                                                        os.path.join(
                                                            gandalfroot,
                                                            user_profile,
                                                            userobject,
                                                            librarysubdir,
                                                            "login.keychain",
                                                        )
                                                    ):
                                                        copy_file(
                                                            os.path.join(
                                                                gandalfroot,
                                                                user_profile,
                                                                userobject,
                                                                librarysubdir,
                                                                "login.keychain",
                                                            ),
                                                            os.path.join(
                                                                gandalf_artefact_destination,
                                                                "user",
                                                                user_profile,
                                                                "login.keychain",
                                                            ),
                                                        )
                                                    else:
                                                        pass
                                                    if os.path.exists(
                                                        os.path.join(
                                                            gandalfroot,
                                                            user_profile,
                                                            userobject,
                                                            librarysubdir,
                                                            "login.keychain",
                                                        )
                                                    ):
                                                        copy_file(
                                                            os.path.join(
                                                                gandalfroot,
                                                                user_profile,
                                                                userobject,
                                                                librarysubdir,
                                                                "login.keychain-db",
                                                            ),
                                                            os.path.join(
                                                                gandalf_artefact_destination,
                                                                "user",
                                                                user_profile,
                                                                "login.keychain-db",
                                                            ),
                                                        )
                                                    else:
                                                        pass
                                                elif librarysubdir == "Mail":
                                                    copy_dir(
                                                        os.path.join(
                                                            gandalfroot,
                                                            user_profile,
                                                            userobject,
                                                            librarysubdir,
                                                        ),
                                                        os.path.join(
                                                            gandalf_artefact_destination,
                                                            "user",
                                                            user_profile,
                                                            librarysubdir,
                                                        ),
                                                    )
                                                elif librarysubdir == "Safari":
                                                    copy_dir(
                                                        os.path.join(
                                                            gandalfroot,
                                                            user_profile,
                                                            userobject,
                                                            librarysubdir,
                                                        ),
                                                        os.path.join(
                                                            gandalf_artefact_destination,
                                                            "user",
                                                            usergandalfroot.split("/")[
                                                                -1
                                                            ],
                                                            librarysubdir,
                                                        ),
                                                    )
                                                    if os.path.exists(
                                                        os.path.join(
                                                            gandalf_artefact_destination,
                                                            "user",
                                                            usergandalfroot.split("/")[
                                                                -1
                                                            ],
                                                            librarysubdir,
                                                            "History.db",
                                                        )
                                                    ):
                                                        collect_browser_artefact(
                                                            os.path.join(
                                                                gandalfroot,
                                                                user_profile,
                                                                userobject,
                                                                librarysubdir,
                                                                "History.db",
                                                            ),
                                                            gandalf_artefact_destination,
                                                            usergandalfroot.split("/")[
                                                                -1
                                                            ],
                                                            "safari",
                                                            "History.db",
                                                        )
                                                        os.remove(
                                                            os.path.join(
                                                                gandalf_artefact_destination,
                                                                "user",
                                                                user_profile,
                                                                "safari",
                                                                "History.db",
                                                            )
                                                        )
                                                        print(
                                                            "      \033[1;32mAcquired 'safari' browser artefacts for '{}' from '{}'\033[1;m".format(
                                                                artefact_output_dir,
                                                                gandalf_artefact_destination.split(
                                                                    "/"
                                                                )[
                                                                    -2
                                                                ],
                                                                gandalf_artefact_destination.split(
                                                                    "/"
                                                                )[
                                                                    -4
                                                                ],
                                                            )
                                                        )
                                                    else:
                                                        pass
                                                elif (
                                                    librarysubdir
                                                    == "Application Support"
                                                ):
                                                    for applicationdir in os.listdir(
                                                        os.path.join(
                                                            userlibraryroot,
                                                            librarysubdir,
                                                        )
                                                    ):
                                                        if applicationdir == "Google":
                                                            if os.path.exists(
                                                                os.path.join(
                                                                    userlibraryroot,
                                                                    librarysubdir,
                                                                    applicationdir,
                                                                    "Chrome",
                                                                    "Default",
                                                                    "History",
                                                                )
                                                            ):
                                                                collect_browser_artefact(
                                                                    os.path.join(
                                                                        gandalfroot,
                                                                        user_profile,
                                                                        userobject,
                                                                        librarysubdir,
                                                                        applicationdir,
                                                                        "Chrome",
                                                                        "Default",
                                                                        "History",
                                                                    ),
                                                                    gandalf_artefact_destination,
                                                                    usergandalfroot.split(
                                                                        "/"
                                                                    )[
                                                                        -1
                                                                    ],
                                                                    "Chrome",
                                                                    "History",
                                                                )
                                                        elif (
                                                            applicationdir == "Firefox"
                                                        ):
                                                            if os.path.exists(
                                                                os.path.join(
                                                                    userlibraryroot,
                                                                    librarysubdir,
                                                                    applicationdir,
                                                                    "Firefox",
                                                                    "Profiles",
                                                                )
                                                            ):
                                                                for (
                                                                    profile
                                                                ) in os.path.join(
                                                                    userlibraryroot,
                                                                    librarysubdir,
                                                                    applicationdir,
                                                                    "Firefox",
                                                                    "Profiles",
                                                                ):
                                                                    if os.path.exists(
                                                                        os.path.join(
                                                                            userlibraryroot,
                                                                            librarysubdir,
                                                                            applicationdir,
                                                                            "Firefox",
                                                                            "Profiles",
                                                                            profile,
                                                                            "places.sqlite",
                                                                        )
                                                                    ):
                                                                        collect_browser_artefact(
                                                                            os.path.join(
                                                                                gandalfroot,
                                                                                user_profile,
                                                                                userobject,
                                                                                librarysubdir,
                                                                                applicationdir,
                                                                                "Firefox",
                                                                                "Profiles",
                                                                                profile,
                                                                                "places.sqlite",
                                                                            ),
                                                                            gandalf_artefact_destination,
                                                                            usergandalfroot.split(
                                                                                "/"
                                                                            )[
                                                                                -1
                                                                            ],
                                                                            "Firefox",
                                                                            "places.sqlite",
                                                                        )
                                                                    else:
                                                                        pass
                                                            else:
                                                                pass
                                                        else:
                                                            pass
                                                else:
                                                    pass
                                        else:
                                            pass
                        else:
                            pass
                    else:
                        pass
        else:
            pass
        previously_collected = print_progress(
            artefact,
            gandalf_host.split("/")[-1],
            artefact_output_dir,
            previously_collected,
        )
    for collected_root, collected_dirs, collected_files in os.walk(gandalf_destination):
        for collected_dir in collected_dirs:
            os.chmod(os.path.join(collected_root, collected_dir), 0o755)
        for collected_file in collected_files:
            os.chmod(os.path.join(collected_root, collected_file), 0o755)
    os.chmod(gandalf_destination, 0o755)
    archive_artefacts(encryption, gandalf_destination, gandalf_host)
