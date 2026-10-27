

# SwitchAudioSource [-a] [-c] [-f format] [-t type] [-n] -s device_name | -i device_id | -u device_uid

# -a : shows all devices
# -c : shows current device
# -f format : output format (cli/human/json). Defaults to human.
# -t type : device type (input/output/system). Defaults to output.
# -m mute_mode : sets the mute status (mute/unmute/toggle).
# -n : cycles the audio device to the next one
# -i device_id : sets the audio device to the given device by id
# -u device_uid : sets the audio device to the given device by uid or a substring of the uid
# -s device_name : sets the audio device to the given device by name


# SwitchAudioSource -a
#     BlackHole 16ch
#     MacBook Pro-mikrofon
#     Microsoft Teams Audio
#     ZoomAudioDevice
#     Sammanslagen enhet
#     U32J59x
#     BlackHole 16ch
#     Högtalare i MacBook Pro
#     Microsoft Teams Audio
#     ZoomAudioDevice
#     Sammanslagen enhet


# SwitchAudioSource -a # shows all devices
# SwitchAudioSource -c # shows current device
# -f # format (human)
# -i 

# device_id
# device_uid
# device_name

# $ SwitchAudioSource -s "BlackHole 16ch"
# output audio device set to "BlackHole 16ch"

# $ SwitchAudioSource -s "Högtalare i MacBook Pro"
# output audio device set to "Högtalare i MacBook Pro"