Running nio upon startup in ubuntu
----------------------------------


    Assumption: run_nio executable-flag is set (chmod)

* Simplest way:

    Add run_nio to /etc/rc.local file e.g.,

    run_nio &

    where & at the end makes the script go to background

* Add run_nio script to /etc/init.d and then run the command:

    > update-rc.d run_nio defaults

    Note: if you wish to remove the script from the startup sequence in the future run:

    > update-rc.d -f run_nio remove

