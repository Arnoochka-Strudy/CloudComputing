import jenkins.model.*
import hudson.model.*
import hudson.tools.*
import jenkins.plugins.nodejs.tools.*
import hudson.plugins.groovy.*
import hudson.tasks.Maven.MavenInstaller
import hudson.tasks.Maven.MavenInstallation
import hudson.plugins.gradle.GradleInstaller
import hudson.plugins.gradle.GradleInstallation
import jenkins.plugins.nodejs.NodeJSInstaller
import jenkins.plugins.nodejs.tools.NodeJSInstallation

// Установка Python
def pythonInstaller = new hudson.plugins.python.PythonInstaller("3.11.0")
def pythonInstallation = new hudson.plugins.python.PythonInstallation("Python3", "", [pythonInstaller])
def jenkins = Jenkins.getInstance()
def pythonExtension = jenkins.getExtensionList(hudson.plugins.python.PythonInstallation.DescriptorImpl.class)[0]
pythonExtension.setInstallations(pythonInstallation)

// Настройка Docker
import com.nirima.jenkins.plugins.docker.*
import com.github.dockerjava.api.DockerClient
import com.github.dockerjava.core.*

// Настройка облака Docker
def dockerCloud = new DockerCloud(
    "docker-cloud",
    [new DockerTemplate(
        new DockerTemplateBase(
            "docker:latest", // Используем образ docker:dind для агентов
            "", // credentialsId
            "", // host
            "", // serverUrl
            10, // connectTimeout
            10, // readTimeout
            "", // version
            1, // dockerCommand
            "", // volumes
            "", // volumesFrom
            "", // environment
            "", // dnsHosts
            "", // group
            "", // bindPorts
            true, // bindAllPorts
            false, // privileged
            false, // tty
            "", // macAddress
            "", // extraHosts
            "", // network
            "", // cpusetCpus
            "", // cpusetMems
            0, // cpuShares
            0, // memoryLimit
            0, // memorySwap
            "", // shmSize
            false, // disableNetwork
            "", // extraGroups
            "", // devices
            "" // restartPolicy
        )
    )],
    "http://localhost:2375", // Docker Host URL
    100, // containerCap
    10, // connectTimeout
    10, // readTimeout
    "", // credentialsId
    "" // version
)

// Сохраняем настройки
jenkins.clouds.replace(dockerCloud)
jenkins.save()